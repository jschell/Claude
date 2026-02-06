<#
.SYNOPSIS
    GUI automation helper functions for Windows

.DESCRIPTION
    Provides Click-At, Type-Text, Focus-Window, and other GUI automation primitives.

.EXAMPLE
    . .\gui-helper.ps1
    Focus-Window -Name "*Epomaker*"
    Click-At -X 100 -Y 200
    Type-Text -Text "Hello"
#>

# Load required assemblies
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Import user32.dll for mouse and window functions
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    public const int MOUSEEVENTF_LEFTDOWN = 0x02;
    public const int MOUSEEVENTF_LEFTUP = 0x04;
    public const int MOUSEEVENTF_RIGHTDOWN = 0x08;
    public const int MOUSEEVENTF_RIGHTUP = 0x10;
    public const int SW_RESTORE = 9;
}
"@

function Focus-Window {
    <#
    .SYNOPSIS
        Finds and focuses a window by title pattern
    .PARAMETER Name
        Window title pattern (supports wildcards)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )

    $proc = Get-Process | Where-Object { $_.MainWindowTitle -like $Name } | Select-Object -First 1

    if ($proc) {
        [Win32]::ShowWindow($proc.MainWindowHandle, [Win32]::SW_RESTORE)
        [Win32]::SetForegroundWindow($proc.MainWindowHandle)
        Start-Sleep -Milliseconds 200
        return $true
    }

    Write-Warning "Window not found: $Name"
    return $false
}

function Click-At {
    <#
    .SYNOPSIS
        Moves mouse to coordinates and clicks
    .PARAMETER X
        X coordinate (absolute screen position)
    .PARAMETER Y
        Y coordinate (absolute screen position)
    .PARAMETER Right
        Perform right-click instead of left-click
    .PARAMETER Double
        Perform double-click
    #>
    param(
        [Parameter(Mandatory=$true)]
        [int]$X,
        [Parameter(Mandatory=$true)]
        [int]$Y,
        [switch]$Right,
        [switch]$Double
    )

    # Move cursor
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($X, $Y)
    Start-Sleep -Milliseconds 50

    # Click
    if ($Right) {
        [Win32]::mouse_event([Win32]::MOUSEEVENTF_RIGHTDOWN -bor [Win32]::MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    } else {
        [Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTDOWN -bor [Win32]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        if ($Double) {
            Start-Sleep -Milliseconds 50
            [Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTDOWN -bor [Win32]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        }
    }
}

function Type-Text {
    <#
    .SYNOPSIS
        Types text using SendKeys
    .PARAMETER Text
        Text to type
    .PARAMETER Raw
        Send without special key interpretation
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Text,
        [switch]$Raw
    )

    if ($Raw) {
        # Escape special SendKeys characters
        $escaped = $Text -replace '([+^%~(){}[\]])', '{$1}'
        [System.Windows.Forms.SendKeys]::SendWait($escaped)
    } else {
        [System.Windows.Forms.SendKeys]::SendWait($Text)
    }
}

function Send-Key {
    <#
    .SYNOPSIS
        Sends special keys or key combinations
    .PARAMETER Key
        Key to send (e.g., "ENTER", "TAB", "F1")
    .PARAMETER Ctrl
        Hold Ctrl modifier
    .PARAMETER Shift
        Hold Shift modifier
    .PARAMETER Alt
        Hold Alt modifier
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Key,
        [switch]$Ctrl,
        [switch]$Shift,
        [switch]$Alt
    )

    $combo = ""
    if ($Ctrl)  { $combo += "^" }
    if ($Shift) { $combo += "+" }
    if ($Alt)   { $combo += "%" }

    # Wrap in braces if it's a named key
    if ($Key -match "^[A-Z0-9]+$" -and $Key.Length -gt 1) {
        $combo += "{$Key}"
    } else {
        $combo += $Key
    }

    [System.Windows.Forms.SendKeys]::SendWait($combo)
}

function Get-MousePosition {
    <#
    .SYNOPSIS
        Returns current mouse position
    #>
    $pos = [System.Windows.Forms.Cursor]::Position
    return @{ X = $pos.X; Y = $pos.Y }
}

function Watch-MousePosition {
    <#
    .SYNOPSIS
        Continuously displays mouse position (for coordinate discovery)
    .PARAMETER IntervalMs
        Update interval in milliseconds
    #>
    param(
        [int]$IntervalMs = 500
    )

    Write-Host "Watching mouse position. Press Ctrl+C to stop." -ForegroundColor Yellow
    Write-Host ""

    try {
        while ($true) {
            $pos = Get-MousePosition
            Write-Host "`rX: $($pos.X.ToString().PadLeft(4))  Y: $($pos.Y.ToString().PadLeft(4))" -NoNewline
            Start-Sleep -Milliseconds $IntervalMs
        }
    } finally {
        Write-Host ""
    }
}

function Wait-Window {
    <#
    .SYNOPSIS
        Waits for a window to appear
    .PARAMETER Name
        Window title pattern
    .PARAMETER TimeoutSeconds
        Maximum wait time
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,
        [int]$TimeoutSeconds = 30
    )

    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        $proc = Get-Process | Where-Object { $_.MainWindowTitle -like $Name }
        if ($proc) {
            return $true
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }

    Write-Warning "Timeout waiting for window: $Name"
    return $false
}

# Export for module use
Export-ModuleMember -Function Focus-Window, Click-At, Type-Text, Send-Key, Get-MousePosition, Watch-MousePosition, Wait-Window
