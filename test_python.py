import sys
import subprocess

print("Current Python:", sys.executable)
print("Python version:", sys.version)

# Try to find other Python installations
try:
    result = subprocess.run(['which', 'python3.13'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Found python3.13 at:", result.stdout.strip())
except:
    pass

try:
    result = subprocess.run(['which', 'python3.12'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Found python3.12 at:", result.stdout.strip())
except:
    pass

# Check if we can import Flask
try:
    import flask
    print("Flask is available in this Python environment")
    print("Flask version:", flask.__version__)
except ImportError:
    print("Flask is NOT available in this Python environment")
