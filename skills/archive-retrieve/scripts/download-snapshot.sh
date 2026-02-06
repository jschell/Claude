#!/bin/bash
# Download specific archived snapshot

if [ -z "$1" ]; then
    echo "Usage: download-snapshot.sh <url> [timestamp|latest]"
    echo "  timestamp format: YYYYMMDDHHMMSS or YYYYMMDD"
    exit 1
fi

url=$1
timestamp=${2:-latest}

if [ "$timestamp" = "latest" ]; then
    echo "Finding latest snapshot..."
    response=$(curl -s "https://archive.org/wayback/available?url=$url")
    snapshot=$(echo "$response" | grep -o '"url": "[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -z "$snapshot" ]; then
        echo "✗ No snapshot available for: $url"
        exit 1
    fi
else
    snapshot="https://web.archive.org/web/${timestamp}id_/$url"
fi

outfile="snapshot_${timestamp}.html"
echo "Downloading: $snapshot"

curl -sL "$snapshot" -o "$outfile"

if [ -s "$outfile" ]; then
    echo "✓ Downloaded to: $outfile"
    echo "  Size: $(wc -c < "$outfile") bytes"
else
    echo "✗ Download failed or empty response"
    rm -f "$outfile"
    exit 1
fi
