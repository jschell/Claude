# Epomaker Keyboard Software Automation

Windows-only automation for Epomaker RT keyboard configuration software.

## Prerequisites

```powershell
# Verify Epomaker is installed
Test-Path "C:\Program Files\Epomaker\Epomaker RT.exe"
Test-Path "$env:LOCALAPPDATA\Programs\Epomaker\Epomaker RT.exe"
```

## Launch Application

```powershell
# Start Epomaker RT
$paths = @(
    "C:\Program Files\Epomaker\Epomaker RT.exe",
    "$env:LOCALAPPDATA\Programs\Epomaker\Epomaker RT.exe"
)
foreach ($path in $paths) {
    if (Test-Path $path) {
        Start-Process $path
        break
    }
}

# Wait for window
Start-Sleep -Seconds 3
```

## Focus Window

```powershell
$epomaker = Get-Process | Where-Object { $_.MainWindowTitle -like "*Epomaker*" }
if ($epomaker) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@
    [Win32]::SetForegroundWindow($epomaker.MainWindowHandle)
}
```

## Common UI Elements

> **Note:** Coordinates vary by screen resolution and window position. These are approximate for 1920x1080 with maximized window.

| Element | Approximate Location | Notes |
|---------|---------------------|-------|
| Profile tabs | Top bar | Usually Tab 1-3 |
| RGB section | Left sidebar | Lighting controls |
| Key mapping | Center area | Click key to remap |
| Macro editor | Right panel | After selecting key |
| Apply button | Bottom right | Saves changes |
| Device selector | Top left dropdown | If multiple keyboards |

## Common Workflows

### Change RGB Lighting Mode

```powershell
# 1. Focus window
# 2. Click RGB/Lighting tab (coordinates needed from user)
# 3. Select effect from dropdown
# 4. Click Apply

param(
    [int]$LightingTabX = 150,
    [int]$LightingTabY = 100,
    [int]$EffectDropdownX = 300,
    [int]$EffectDropdownY = 200,
    [int]$ApplyX = 1800,
    [int]$ApplyY = 1000
)

# Helper function
function Click-At {
    param([int]$X, [int]$Y)
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($X, $Y)
    Start-Sleep -Milliseconds 100

    Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int i);' -Name U -Namespace W
    [W.U]::mouse_event(6,0,0,0,0)  # Left click
}

Click-At -X $LightingTabX -Y $LightingTabY
Start-Sleep -Milliseconds 500
Click-At -X $EffectDropdownX -Y $EffectDropdownY
Start-Sleep -Milliseconds 300
# Select effect (arrow keys + enter)
[System.Windows.Forms.SendKeys]::SendWait("{DOWN}{DOWN}{ENTER}")
Start-Sleep -Milliseconds 300
Click-At -X $ApplyX -Y $ApplyY
```

### Switch Profile

```powershell
param([int]$ProfileNumber = 1)

# Click profile tab (adjust coordinates)
$profileTabs = @{
    1 = @{X=100; Y=50}
    2 = @{X=200; Y=50}
    3 = @{X=300; Y=50}
}

$tab = $profileTabs[$ProfileNumber]
Click-At -X $tab.X -Y $tab.Y
```

## Coordinate Discovery

Run this script, then hover over UI elements:

```powershell
Add-Type -AssemblyName System.Windows.Forms
Write-Host "Move mouse to UI elements. Press Ctrl+C to stop."
Write-Host "Recording coordinates..."

while($true) {
    $pos = [System.Windows.Forms.Cursor]::Position
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] X: $($pos.X), Y: $($pos.Y)"
    Start-Sleep -Milliseconds 500
}
```

Save coordinates for your specific setup in a config file:

```powershell
# epomaker-coords.json
@{
    "resolution" = "1920x1080"
    "window" = "maximized"
    "elements" = @{
        "profile1" = @{x=100; y=50}
        "profile2" = @{x=200; y=50}
        "rgb_tab" = @{x=150; y=100}
        "apply_btn" = @{x=1800; y=1000}
    }
} | ConvertTo-Json | Set-Content "epomaker-coords.json"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Window not found | Check process name: `Get-Process \| Where-Object {$_.MainWindowTitle -ne ""}` |
| Clicks miss target | Re-capture coordinates for your resolution |
| Actions too fast | Increase `Start-Sleep` delays |
| App not responding | Try running PowerShell as Administrator |
| Multiple monitors | Coordinates are absolute across all displays |

## Version Compatibility

| Epomaker RT Version | Tested | Notes |
|---------------------|--------|-------|
| 1.x | Untested | Older UI layout |
| 2.x | Target | Current version |

> **Important:** UI layouts change between versions. Re-capture coordinates after updates.
