import urllib.request
import os
import subprocess

# Define the URL of the file
url = "https://raw.githubusercontent.com/vikramiiitm/testfile/refs/heads/main/main.py"

# Send GET request to download the file
response = urllib.request.urlopen(url)

# Check if the request was successful
if response.getcode() == 200:
  # Get the filename from the response headers (optional)
  filename = response.info().get('Content-Disposition')
#   if filename:
#     filename = filename.split('=')[1].strip('"')
#   else:
    # If filename unavailable, use a generic filename
  filename = "main3.py"

  # Open the file in write binary mode
  with open(filename, "wb") as f:
    f.write(response.read())

  print(f"File downloaded successfully: {filename}")
else:
  print(f"Download failed with status code: {response.getcode()}")


subprocess.run(["python", "main3.py"]) # Run the downloaded script

# Remove the downloaded script file
os.remove(filename)
# check if the file was removed successfully
if not os.path.exists(filename):
   print(f"terminated: {filename}")
else:
    print(f"not terminated: {filename}")

# Print completion message
print("Script execution completed.")