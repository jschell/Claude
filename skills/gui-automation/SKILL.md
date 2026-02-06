---
name: gui-automation
description: Use when automating desktop GUI interactions - window management, clicking, typing, keyboard configuration tools like Epomaker
---

# GUI Automation

> **Limitation:** Claude Code runs in terminal without screen access. GUI automation requires spawning scripts that interact with the desktop.

## Platform Tools

| Platform | Tool | Install |
|----------|------|---------|
| Windows | PowerShell + SendKeys/UIAutomation | Built-in |
| macOS | AppleScript / cliclick | `brew install cliclick` |
| Linux | xdotool / ydotool (Wayland) | `apt install xdotool` |

## Core Operations

### Find and Focus Window

```powershell
# Windows - by process name
$proc = Get-Process | Where-Object { $_.MainWindowTitle -like "*Epomaker*" }
if ($proc) {
    Add-Type @"
    using System; using System.Runtime.InteropServices;
    public class Win32 { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd); }
"@
    [Win32]::SetForegroundWindow($proc.MainWindowHandle)
}
```

```bash
# macOS
osascript -e 'tell application "Epomaker" to activate'

# Linux
xdotool search --name "Epomaker" windowactivate
```

### Click at Position

```powershell
# Windows
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(X, Y)
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

# Or use mouse_event for actual click
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int i);' -Name U -Namespace W
[W.U]::mouse_event(6,0,0,0,0)  # Left click (down+up = 2+4)
```

```bash
# macOS
cliclick c:100,200

# Linux
xdotool mousemove 100 200 click 1
```

### Type Text / Send Keys

```powershell
# Windows - SendKeys
[System.Windows.Forms.SendKeys]::SendWait("Hello World")
[System.Windows.Forms.SendKeys]::SendWait("{TAB}{ENTER}")  # Special keys
```

```bash
# macOS
osascript -e 'tell application "System Events" to keystroke "Hello"'

# Linux
xdotool type "Hello World"
```

## Workflow Pattern

```
1. Launch app (if not running)
2. Wait for window (sleep/retry loop)
3. Focus window
4. Navigate to target (clicks/tabs)
5. Perform action
6. Verify if possible (window title change, etc.)
```

## Coordinate Discovery

Since Claude can't see the screen, coordinates must be provided:

```powershell
# Windows - show current mouse position (run manually)
Add-Type -AssemblyName System.Windows.Forms
while($true) {
    $p = [System.Windows.Forms.Cursor]::Position
    Write-Host "X: $($p.X) Y: $($p.Y)"
    Start-Sleep -Milliseconds 500
}
```

## Limitations

| Issue | Mitigation |
|-------|------------|
| No screen visibility | User provides coordinates or element names |
| Resolution-dependent | Use relative positions or UI Automation |
| Timing-sensitive | Add delays between actions |
| App updates break scripts | Document UI version tested |

## See Also

- [Platform Tools](references/platform-tools.md)
- [Epomaker Automation](references/epomaker.md)
