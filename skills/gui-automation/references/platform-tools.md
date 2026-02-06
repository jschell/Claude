# Platform-Specific GUI Automation Tools

## Windows

### Built-in: PowerShell + .NET

```powershell
# Load Windows Forms for mouse/keyboard
Add-Type -AssemblyName System.Windows.Forms

# Mouse position
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(100, 200)

# Send keystrokes
[System.Windows.Forms.SendKeys]::SendWait("text")
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
[System.Windows.Forms.SendKeys]::SendWait("^c")  # Ctrl+C
```

### SendKeys Special Keys

| Key | Code | Key | Code |
|-----|------|-----|------|
| Enter | `{ENTER}` | Tab | `{TAB}` |
| Escape | `{ESC}` | Backspace | `{BACKSPACE}` |
| Delete | `{DELETE}` | Arrow Up | `{UP}` |
| Arrow Down | `{DOWN}` | Arrow Left | `{LEFT}` |
| Arrow Right | `{RIGHT}` | Home | `{HOME}` |
| End | `{END}` | Page Up | `{PGUP}` |
| F1-F12 | `{F1}`-`{F12}` | | |

**Modifiers:** `^` = Ctrl, `+` = Shift, `%` = Alt

```powershell
[System.Windows.Forms.SendKeys]::SendWait("^s")      # Ctrl+S
[System.Windows.Forms.SendKeys]::SendWait("+{TAB}")  # Shift+Tab
[System.Windows.Forms.SendKeys]::SendWait("%{F4}")   # Alt+F4
```

### UI Automation (Robust)

```powershell
# More reliable than coordinates - finds elements by properties
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty, "Apply"
)
$button = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)

if ($button) {
    $invokePattern = $button.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()
}
```

---

## macOS

### AppleScript

```bash
# Keystroke
osascript -e 'tell application "System Events" to keystroke "hello"'

# Key code (special keys)
osascript -e 'tell application "System Events" to key code 36'  # Enter

# Click (requires Accessibility permissions)
osascript -e 'tell application "System Events" to click at {100, 200}'
```

### cliclick (Recommended)

```bash
# Install
brew install cliclick

# Click
cliclick c:100,200       # Click at coordinates
cliclick dc:100,200      # Double-click
cliclick rc:100,200      # Right-click

# Type
cliclick t:"Hello World"

# Move
cliclick m:100,200

# Keyboard
cliclick kp:enter        # Press Enter
cliclick kd:cmd kp:s ku:cmd  # Cmd+S
```

---

## Linux

### xdotool (X11)

```bash
# Install
sudo apt install xdotool  # Debian/Ubuntu
sudo dnf install xdotool  # Fedora

# Click
xdotool mousemove 100 200 click 1    # Left click
xdotool mousemove 100 200 click 3    # Right click

# Type
xdotool type "Hello World"

# Key
xdotool key Return
xdotool key ctrl+s
xdotool key alt+F4

# Window management
xdotool search --name "Firefox" windowactivate
xdotool getactivewindow getwindowname
```

### ydotool (Wayland)

```bash
# Install
sudo apt install ydotool

# Requires ydotoold daemon
sudo ydotoold &

# Click
ydotool mousemove -x 100 -y 200
ydotool click 1

# Type
ydotool type "Hello World"

# Key
ydotool key enter
```

---

## Cross-Platform Python

### PyAutoGUI

```bash
pip install pyautogui
```

```python
import pyautogui
import time

# Safety feature - move to corner to abort
pyautogui.FAILSAFE = True

# Click
pyautogui.click(100, 200)
pyautogui.doubleClick(100, 200)
pyautogui.rightClick(100, 200)

# Type
pyautogui.write('Hello World')
pyautogui.press('enter')
pyautogui.hotkey('ctrl', 's')

# Mouse
pyautogui.moveTo(100, 200)
pyautogui.moveRel(50, 0)  # Relative

# Screen
x, y = pyautogui.position()
width, height = pyautogui.size()
```

---

## Comparison

| Feature | Windows PS | macOS AS | cliclick | xdotool | PyAutoGUI |
|---------|------------|----------|----------|---------|-----------|
| Click | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| Type | ✅ | ✅ | ✅ | ✅ | ✅ |
| Window focus | ✅ | ✅ | ❌ | ✅ | ⚠️ |
| Find by name | ✅* | ✅ | ❌ | ✅ | ❌ |
| Cross-platform | ❌ | ❌ | ❌ | ❌ | ✅ |

*With UI Automation API
