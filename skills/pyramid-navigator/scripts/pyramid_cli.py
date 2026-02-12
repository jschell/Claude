#!/usr/bin/env python3
"""pyramid_cli.py - Pyramid Summary Generator CLI

Indexes a codebase with multi-level LLM summaries for progressive navigation.

Usage:
  python pyramid_cli.py init                     # Initialize in current directory
  python pyramid_cli.py analyze [PATH]           # Index codebase
  python pyramid_cli.py query QUERY [--level N]  # Search summaries
  python pyramid_cli.py get ELEMENT_PATH         # Get specific element
  python pyramid_cli.py list [--level N]         # List all elements

Storage (.pyramid/):
  config.json       - Project configuration
  index.json        - Fast search index (levels 4, 8, 16 only)
  data/<sha>.json   - Full element data (all levels + code)

Environment:
  ANTHROPIC_API_KEY  - Required for Anthropic (default)
  OPENAI_API_KEY     - Required for OpenAI (use --api openai)
  PYRAMID_DB         - Override .pyramid/ directory location
"""

import sys
import json
import hashlib
import re
import os
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Optional

import click

# ─────────────────────────────────────────────
# SECTION: Data structures
# ─────────────────────────────────────────────

@dataclass
class Element:
    """A parsed code element (file, class, or function)."""
    path: str          # Relative path from project root
    element_type: str  # "file", "class", "function"
    name: str          # Element name (filename for files)
    code: str          # Raw source code
    start_line: int
    end_line: int

    def content_hash(self) -> str:
        return hashlib.sha256(self.code.encode()).hexdigest()


# ─────────────────────────────────────────────
# SECTION: Storage
# ─────────────────────────────────────────────

class StorageManager:
    """Read/write .pyramid/ directory."""

    VERSION = 1

    def __init__(self, pyramid_dir: Path):
        self.pyramid_dir = pyramid_dir
        self.data_dir = pyramid_dir / "data"
        self.index_path = pyramid_dir / "index.json"
        self.config_path = pyramid_dir / "config.json"

    def init(self, api: str = "anthropic") -> None:
        """Create .pyramid/ structure."""
        self.pyramid_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        if not self.config_path.exists():
            self._write_json(self.config_path, {
                "version": self.VERSION,
                "created": datetime.now(timezone.utc).isoformat(),
                "api": api,
            })

        if not self.index_path.exists():
            self._write_json(self.index_path, {})

    def is_initialized(self) -> bool:
        return self.pyramid_dir.exists() and self.index_path.exists()

    def load_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        return self._read_json(self.config_path)

    def load_index(self) -> dict:
        if not self.index_path.exists():
            return {}
        return self._read_json(self.index_path)

    def save_index(self, index: dict) -> None:
        self._write_json(self.index_path, index)

    def load_data(self, sha: str) -> Optional[dict]:
        path = self.data_dir / f"{sha}.json"
        if not path.exists():
            return None
        return self._read_json(path)

    def save_data(self, sha: str, data: dict) -> None:
        path = self.data_dir / f"{sha}.json"
        self._write_json(path, data)

    @staticmethod
    def _read_json(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
# SECTION: Parser
# ─────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
}

IGNORE_DIRS = {
    ".git", ".pyramid", "__pycache__", "node_modules", ".venv", "venv",
    "env", ".env", "dist", "build", "target", ".tox", ".pytest_cache",
    ".mypy_cache", "coverage", ".coverage", "htmlcov",
}

IGNORE_FILES = {
    "*.min.js", "*.min.css", "*.lock", "package-lock.json", "yarn.lock",
    "Pipfile.lock", "poetry.lock",
}


def _should_ignore_file(path: Path) -> bool:
    name = path.name
    for pattern in IGNORE_FILES:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


class CodeParser:
    """Extract code elements from source files."""

    def __init__(self):
        self._ts_available = self._check_tree_sitter()

    @staticmethod
    def _check_tree_sitter() -> bool:
        try:
            import tree_sitter_languages  # noqa: F401
            return True
        except ImportError:
            return False

    def parse_file(self, path: Path, root: Path) -> list[Element]:
        """Parse a file and return its elements. Always includes file-level element."""
        relative = str(path.relative_to(root))
        suffix = path.suffix.lower()

        try:
            code = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        lines = code.splitlines()
        elements = [Element(
            path=relative,
            element_type="file",
            name=path.name,
            code=code,
            start_line=1,
            end_line=len(lines),
        )]

        if suffix not in SUPPORTED_EXTENSIONS:
            return elements

        lang = SUPPORTED_EXTENSIONS[suffix]

        if self._ts_available:
            sub_elements = self._parse_tree_sitter(code, relative, lang)
        else:
            sub_elements = self._parse_heuristic(code, relative, suffix)

        elements.extend(sub_elements)
        return elements

    def _parse_tree_sitter(self, code: str, relative: str, lang: str) -> list[Element]:
        try:
            from tree_sitter_languages import get_language, get_parser
            language = get_language(lang)
            parser = get_parser(lang)
        except Exception:
            return []

        tree = parser.parse(code.encode())
        elements = []
        lines = code.splitlines()

        # Node types per language for functions and classes
        func_types = {
            "python": ["function_definition", "async_function_definition"],
            "javascript": ["function_declaration", "arrow_function", "method_definition"],
            "typescript": ["function_declaration", "arrow_function", "method_definition"],
            "go": ["function_declaration", "method_declaration"],
            "rust": ["function_item"],
            "java": ["method_declaration", "constructor_declaration"],
            "c": ["function_definition"],
            "cpp": ["function_definition"],
            "ruby": ["method"],
            "php": ["function_definition", "method_declaration"],
        }

        class_types = {
            "python": ["class_definition"],
            "javascript": ["class_declaration"],
            "typescript": ["class_declaration"],
            "java": ["class_declaration"],
            "ruby": ["class"],
            "php": ["class_declaration"],
            "rust": ["impl_item", "struct_item"],
            "go": ["type_declaration"],
            "c": ["struct_specifier"],
            "cpp": ["class_specifier", "struct_specifier"],
        }

        lang_func_types = set(func_types.get(lang, []))
        lang_class_types = set(class_types.get(lang, []))

        def extract_name(node) -> str:
            # Look for identifier or name child node
            for child in node.children:
                if child.type in ("identifier", "name", "field_identifier", "property_identifier"):
                    return child.text.decode() if child.text else ""
            return node.type

        def walk(node):
            if node.type in lang_func_types:
                name = extract_name(node)
                start = node.start_point[0]
                end = node.end_point[0]
                snippet = "\n".join(lines[start:end + 1])
                elements.append(Element(
                    path=relative,
                    element_type="function",
                    name=name,
                    code=snippet,
                    start_line=start + 1,
                    end_line=end + 1,
                ))
            elif node.type in lang_class_types:
                name = extract_name(node)
                start = node.start_point[0]
                end = node.end_point[0]
                snippet = "\n".join(lines[start:end + 1])
                elements.append(Element(
                    path=relative,
                    element_type="class",
                    name=name,
                    code=snippet,
                    start_line=start + 1,
                    end_line=end + 1,
                ))
            for child in node.children:
                walk(child)

        walk(tree.root_node)
        return elements

    def _parse_heuristic(self, code: str, relative: str, suffix: str) -> list[Element]:
        """Fallback line-based parser for unsupported languages."""
        elements = []
        lines = code.splitlines()

        # Patterns per file type
        if suffix == ".py":
            func_pat = re.compile(r"^(async\s+)?def\s+(\w+)\s*\(")
            class_pat = re.compile(r"^class\s+(\w+)")
        elif suffix in (".js", ".ts"):
            func_pat = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|^\s*(\w+)\s*[:=]\s*(?:async\s+)?(?:function|\()")
            class_pat = re.compile(r"^(?:export\s+)?class\s+(\w+)")
        elif suffix == ".go":
            func_pat = re.compile(r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(")
            class_pat = re.compile(r"^type\s+(\w+)\s+struct")
        elif suffix == ".rs":
            func_pat = re.compile(r"^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*[<(]")
            class_pat = re.compile(r"^(?:pub\s+)?(?:struct|impl|enum)\s+(\w+)")
        else:
            # Generic: look for common patterns
            func_pat = re.compile(r"^(?:def|func|function|fn|sub|procedure)\s+(\w+)")
            class_pat = re.compile(r"^(?:class|struct|interface|type)\s+(\w+)")

        def find_block_end(start_idx: int) -> int:
            """Find end of block by indentation or brace counting."""
            if start_idx >= len(lines):
                return start_idx
            base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
            brace_count = lines[start_idx].count("{") - lines[start_idx].count("}")
            for i in range(start_idx + 1, min(start_idx + 200, len(lines))):
                line = lines[i]
                stripped = line.strip()
                if not stripped:
                    continue
                # Brace-based (C-style)
                if "{" in line or "}" in line:
                    brace_count += line.count("{") - line.count("}")
                    if brace_count <= 0:
                        return i
                else:
                    # Indent-based (Python)
                    indent = len(line) - len(line.lstrip())
                    if indent <= base_indent and stripped:
                        return i - 1
            return min(start_idx + 50, len(lines) - 1)

        for i, line in enumerate(lines):
            m = func_pat.match(line)
            if m:
                name = next((g for g in m.groups() if g and not g.strip() in ("async", "export", "pub")), "unknown")
                name = name.strip()
                end = find_block_end(i)
                snippet = "\n".join(lines[i:end + 1])
                elements.append(Element(
                    path=relative, element_type="function", name=name,
                    code=snippet, start_line=i + 1, end_line=end + 1,
                ))
                continue

            m = class_pat.match(line)
            if m:
                name = m.group(1)
                end = find_block_end(i)
                snippet = "\n".join(lines[i:end + 1])
                elements.append(Element(
                    path=relative, element_type="class", name=name,
                    code=snippet, start_line=i + 1, end_line=end + 1,
                ))

        return elements

    def walk_directory(self, root: Path, ignore_file: Optional[Path] = None) -> list[Path]:
        """Return all parseable source files under root."""
        ignored_patterns = set()
        if ignore_file and ignore_file.exists():
            for line in ignore_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_patterns.add(line)

        # Also read .gitignore patterns (simple subset)
        gitignore = root / ".gitignore"
        if gitignore.exists():
            for line in gitignore.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_patterns.add(line)

        results = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            # Skip ignored directories
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            # Skip ignored files
            if _should_ignore_file(path):
                continue
            # Check .pyramidignore / .gitignore patterns (simple glob)
            rel = str(path.relative_to(root))
            skip = False
            for pat in ignored_patterns:
                pat_clean = pat.lstrip("/")
                if pat_clean in rel or rel.endswith(pat_clean):
                    skip = True
                    break
            if skip:
                continue
            # Only parse supported extensions
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                results.append(path)

        return sorted(results)


# ─────────────────────────────────────────────
# SECTION: Summarizer
# ─────────────────────────────────────────────

SUMMARY_PROMPT = """\
Summarize the following code element at multiple word-count levels.
Return ONLY a JSON object with integer keys matching the requested levels.
Each value must be a plain string with EXACTLY the target word count (count carefully).

Element type: {element_type}
Element name: {name}
File: {path}

Code:
```
{code}
```

Return JSON with these exact word counts: {levels}
Example format: {{"4": "brief four word summary", "8": "slightly longer eight word description here now", "16": "..."}}
"""


class Summarizer:
    """Generate LLM summaries at multiple word-count levels."""

    ANALYZE_LEVELS = [4, 8, 16]
    GET_LEVELS = [32, 64]

    def __init__(self, api: str = "anthropic", model: Optional[str] = None):
        self.api = api
        self.model = model or self._default_model(api)
        self._client = None

    @staticmethod
    def _default_model(api: str) -> str:
        if api == "openai":
            return "gpt-4o-mini"
        return "claude-haiku-4-5-20251001"

    def _get_client(self):
        if self._client is not None:
            return self._client

        if self.api == "openai":
            try:
                import openai
            except ImportError:
                raise SystemExit("openai package required: pip install openai")
            key = os.environ.get("OPENAI_API_KEY")
            if not key:
                raise SystemExit("OPENAI_API_KEY not set")
            self._client = openai.OpenAI(api_key=key)
        else:
            try:
                import anthropic
            except ImportError:
                raise SystemExit("anthropic package required: pip install anthropic")
            key = os.environ.get("ANTHROPIC_API_KEY")
            if not key:
                # Try OpenAI as fallback
                oai_key = os.environ.get("OPENAI_API_KEY")
                if oai_key:
                    click.echo("ANTHROPIC_API_KEY not set, falling back to OpenAI", err=True)
                    self.api = "openai"
                    self.model = self._default_model("openai")
                    return self._get_client()
                raise SystemExit("ANTHROPIC_API_KEY not set (or OPENAI_API_KEY for fallback)")
            self._client = anthropic.Anthropic(api_key=key)

        return self._client

    def summarize(self, element: Element, levels: list[int]) -> dict[str, str]:
        """Call LLM once to get summaries at all requested levels."""
        # Truncate very long code to avoid token limits
        code = element.code
        if len(code) > 8000:
            code = code[:8000] + "\n... (truncated)"

        prompt = SUMMARY_PROMPT.format(
            element_type=element.element_type,
            name=element.name,
            path=element.path,
            code=code,
            levels=levels,
        )

        client = self._get_client()

        try:
            if self.api == "openai":
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=512,
                    temperature=0.1,
                )
                raw = response.choices[0].message.content
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = response.content[0].text

            data = json.loads(raw)
            # Normalize keys to strings
            return {str(k): str(v) for k, v in data.items()}

        except json.JSONDecodeError:
            # Fallback: extract any JSON object from response
            match = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    return {str(k): str(v) for k, v in data.items()}
                except json.JSONDecodeError:
                    pass
            # Last resort: generate stub summaries
            return {str(level): f"{element.element_type} {element.name}" for level in levels}
        except Exception as e:
            click.echo(f"  Warning: LLM error for {element.path}: {e}", err=True)
            return {str(level): f"{element.element_type} {element.name}" for level in levels}


# ─────────────────────────────────────────────
# SECTION: CLI
# ─────────────────────────────────────────────

def _find_pyramid_dir(db_path: Optional[str] = None) -> Path:
    if db_path:
        return Path(db_path)
    env = os.environ.get("PYRAMID_DB")
    if env:
        return Path(env)
    return Path.cwd() / ".pyramid"


def _require_initialized(storage: StorageManager) -> None:
    if not storage.is_initialized():
        raise click.ClickException(
            ".pyramid/ not found. Run: python pyramid_cli.py init"
        )


@click.group()
@click.version_option("0.1.0")
def cli():
    """Pyramid Summary Generator — progressive codebase navigation."""
    pass


# ── init ──────────────────────────────────────

@cli.command()
@click.option("--db-path", default=None, help="Override .pyramid/ location")
@click.option("--api", default="anthropic", type=click.Choice(["anthropic", "openai"]),
              help="LLM provider (default: anthropic)")
def init(db_path, api):
    """Initialize pyramid generator in current directory."""
    pyramid_dir = _find_pyramid_dir(db_path)
    storage = StorageManager(pyramid_dir)

    if storage.is_initialized():
        click.echo(f"Already initialized at {pyramid_dir}")
        return

    storage.init(api=api)
    click.echo(f"✓ Initialized pyramid generator")
    click.echo(f"  Database: {pyramid_dir}")
    click.echo(f"  Config:   {pyramid_dir / 'config.json'}")
    click.echo(f"\nNext: python pyramid_cli.py analyze .")


# ── analyze ───────────────────────────────────

@cli.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--db-path", default=None, help="Override .pyramid/ location")
@click.option("--api", default=None, type=click.Choice(["anthropic", "openai"]),
              help="LLM provider override")
@click.option("--model", default=None, help="Override LLM model name")
@click.option("--force", is_flag=True, help="Re-analyze all files, ignoring cache")
@click.option("--workers", default=4, show_default=True, help="Parallel LLM workers")
def analyze(path, db_path, api, model, force, workers):
    """Analyze codebase and generate pyramid summaries."""
    root = Path(path).resolve()
    pyramid_dir = _find_pyramid_dir(db_path)
    storage = StorageManager(pyramid_dir)
    _require_initialized(storage)

    config = storage.load_config()
    effective_api = api or config.get("api", "anthropic")
    summarizer = Summarizer(api=effective_api, model=model)
    parser = CodeParser()

    click.echo(f"Analyzing codebase at: {root}")

    # Collect files
    ignore_file = root / ".pyramidignore"
    files = parser.walk_directory(root, ignore_file)
    click.echo(f"Found {len(files)} source files")

    index = storage.load_index()
    tasks = []  # (element, sha) pairs that need summarization

    # Parse all files, identify what needs summarizing
    all_elements: list[tuple[Element, str]] = []
    for file_path in files:
        for element in parser.parse_file(file_path, root):
            sha = element.content_hash()
            if not force and sha in index:
                continue  # Already indexed and unchanged
            all_elements.append((element, sha))

    if not all_elements:
        click.echo("✓ All files up to date")
        return

    click.echo(f"Summarizing {len(all_elements)} elements...")

    def process_element(item: tuple[Element, str]) -> tuple[str, dict, Element]:
        element, sha = item
        summaries = summarizer.summarize(element, Summarizer.ANALYZE_LEVELS)

        # Write full data record
        data = {
            "path": element.path,
            "element_type": element.element_type,
            "name": element.name,
            "start_line": element.start_line,
            "end_line": element.end_line,
            "code": element.code,
            "levels": summaries,
        }
        storage.save_data(sha, data)

        # Index record (compressed levels only)
        index_entry = {
            "path": element.path,
            "element_type": element.element_type,
            "name": element.name,
            "levels": summaries,
        }
        return sha, index_entry, element

    completed = 0
    with click.progressbar(length=len(all_elements), label="Analyzing") as bar:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_element, item): item for item in all_elements}
            for future in as_completed(futures):
                try:
                    sha, index_entry, element = future.result()
                    index[sha] = index_entry
                    completed += 1
                except Exception as e:
                    elem, _ = futures[future]
                    click.echo(f"\n  Error processing {elem.path}: {e}", err=True)
                bar.update(1)

    storage.save_index(index)
    click.echo(f"\n✓ Analysis complete")
    click.echo(f"  Indexed: {completed} elements")
    click.echo(f"  Database: {pyramid_dir}")


# ── query ─────────────────────────────────────

@cli.command()
@click.argument("query")
@click.option("--level", default=16, type=click.Choice(["4", "8", "16", "32", "64"]),
              help="Word count level to search (default: 16)")
@click.option("--type", "element_type", default=None,
              type=click.Choice(["file", "function", "class"]),
              help="Filter by element type")
@click.option("--db-path", default=None, help="Override .pyramid/ location")
@click.option("--limit", default=20, show_default=True, help="Max results to show")
def query(query, level, element_type, db_path, limit):
    """Search pyramid summaries by keyword."""
    pyramid_dir = _find_pyramid_dir(db_path)
    storage = StorageManager(pyramid_dir)
    _require_initialized(storage)

    index = storage.load_index()
    if not index:
        raise click.ClickException("No indexed elements found. Run: python pyramid_cli.py analyze .")

    query_lower = query.lower()
    results = []

    for sha, entry in index.items():
        if element_type and entry.get("element_type") != element_type:
            continue

        levels = entry.get("levels", {})
        summary = levels.get(str(level), "")

        if query_lower in summary.lower() or query_lower in entry.get("path", "").lower():
            results.append((entry, summary, sha))

    if not results:
        click.echo(f"No results for '{query}' at level {level}")
        if element_type:
            click.echo(f"(filtered by type: {element_type})")
        return

    click.echo(f"Found {len(results)} result(s) for '{query}' (level {level}):\n")
    for entry, summary, sha in results[:limit]:
        path = entry.get("path", "")
        etype = entry.get("element_type", "file")
        name = entry.get("name", "")

        label = path if etype == "file" else f"{path}::{name}"
        click.echo(f"  {label} ({etype})")
        click.echo(f"    {summary}")
        click.echo()

    if len(results) > limit:
        click.echo(f"  ... {len(results) - limit} more results (use --limit to show more)")


# ── get ───────────────────────────────────────

@cli.command()
@click.argument("element_path")
@click.option("--level", default=16, type=click.Choice(["4", "8", "16", "32", "64"]),
              help="Word count level (default: 16)")
@click.option("--show-code", is_flag=True, help="Display actual source code")
@click.option("--db-path", default=None, help="Override .pyramid/ location")
@click.option("--api", default=None, type=click.Choice(["anthropic", "openai"]))
@click.option("--model", default=None)
def get(element_path, level, show_code, db_path, api, model):
    """Get pyramid summary for a specific code element."""
    pyramid_dir = _find_pyramid_dir(db_path)
    storage = StorageManager(pyramid_dir)
    _require_initialized(storage)

    index = storage.load_index()

    # Find matching entries by path prefix
    matches = []
    path_lower = element_path.lower().replace("\\", "/")

    for sha, entry in index.items():
        entry_path = entry.get("path", "").lower().replace("\\", "/")
        if entry_path == path_lower or entry_path.startswith(path_lower):
            matches.append((sha, entry))

    if not matches:
        raise click.ClickException(
            f"No indexed element found for '{element_path}'.\n"
            "Run `python pyramid_cli.py list` to see available paths."
        )

    level_str = str(level)
    level_int = int(level)

    for sha, entry in matches:
        path = entry.get("path", "")
        name = entry.get("name", "")
        etype = entry.get("element_type", "file")
        label = path if etype == "file" else f"{path}::{name}"

        # Check if level already in index (4/8/16)
        cached_summary = entry.get("levels", {}).get(level_str)

        if cached_summary:
            summary = cached_summary
        else:
            # Level 32/64: check data file
            data = storage.load_data(sha)
            if data and level_str in data.get("levels", {}):
                summary = data["levels"][level_str]
            else:
                # Generate on demand
                if data is None:
                    raise click.ClickException(
                        f"Data file missing for {path}. Re-run analyze."
                    )
                config = storage.load_config()
                effective_api = api or config.get("api", "anthropic")
                summarizer = Summarizer(api=effective_api, model=model)
                element = Element(
                    path=path,
                    element_type=etype,
                    name=name,
                    code=data.get("code", ""),
                    start_line=data.get("start_line", 1),
                    end_line=data.get("end_line", 1),
                )
                click.echo(f"Generating level {level} summary...", err=True)
                new_summaries = summarizer.summarize(element, [level_int])
                summary = new_summaries.get(level_str, "")

                # Cache it
                data["levels"][level_str] = summary
                storage.save_data(sha, data)

        click.echo(f"{label} ({level} words):")
        click.echo(f"  {summary}")

        if show_code:
            data = storage.load_data(sha)
            code = data.get("code", "") if data else ""
            if code:
                click.echo()
                click.echo("Code:")
                click.echo("─" * 72)
                click.echo(code)
                click.echo("─" * 72)
        click.echo()


# ── list ──────────────────────────────────────

@cli.command("list")
@click.option("--level", default=4, type=click.Choice(["4", "8", "16"]),
              help="Word count level for summaries (default: 4)")
@click.option("--type", "element_type", default="file",
              type=click.Choice(["file", "function", "class", "all"]),
              help="Filter by element type (default: file)")
@click.option("--db-path", default=None, help="Override .pyramid/ location")
def list_cmd(level, element_type, db_path):
    """List indexed code elements with summaries."""
    pyramid_dir = _find_pyramid_dir(db_path)
    storage = StorageManager(pyramid_dir)
    _require_initialized(storage)

    index = storage.load_index()
    if not index:
        raise click.ClickException("No indexed elements. Run: python pyramid_cli.py analyze .")

    # Group by path for clean display
    seen_paths = {}
    for sha, entry in index.items():
        etype = entry.get("element_type", "file")
        if element_type != "all" and etype != element_type:
            continue
        path = entry.get("path", "")
        summary = entry.get("levels", {}).get(str(level), "")
        name = entry.get("name", "")
        label = path if etype == "file" else f"{path}::{name}"
        seen_paths[label] = (summary, etype)

    if not seen_paths:
        click.echo(f"No {element_type} elements found.")
        return

    click.echo(f"{element_type.capitalize()} elements ({len(seen_paths)} total):\n")
    for label, (summary, etype) in sorted(seen_paths.items()):
        click.echo(f"  {label}")
        if summary:
            click.echo(f"    {summary}")
        click.echo()


if __name__ == "__main__":
    cli()
