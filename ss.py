import subprocess
import time

# Define screenshot filename
screenshot_filename = "screenshot.png"

# Open back camera
adb_command = "adb shell am start -a android.media.action.STILL_IMAGE_CAMERA"
subprocess.run(adb_command.split(), check=True)

# Wait for 1 second
time.sleep(1)

# Zoom in twice
zoom_command = "adb shell input pinch 200 200 200 200 0.5"
subprocess.run(zoom_command.split(), check=True)

# Simulate auto-focus
autofocus_command = "adb shell input tap 500 500"
subprocess.run(autofocus_command.split(), check=True)

# Wait for 2 seconds for auto-focus to complete
time.sleep(2)

# Capture screenshot
adb_command = f"adb shell screencap -p /sdcard/{screenshot_filename}"
subprocess.run(adb_command.split(), check=True)

# Pull screenshot to main.py directory
pull_command = f"adb pull /sdcard/{screenshot_filename} ."
subprocess.run(pull_command.split(), check=True)

print(f"Screenshot saved as: {screenshot_filename}")