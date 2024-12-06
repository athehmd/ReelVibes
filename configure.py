import os
import subprocess
import sys

subprocess.run(["python3", "-m", "virtualenv", "venv"])

if sys.platform == "win32":
     pip_path = os.path.join("venv", "Scripts", "pip3")
else:
    pip_path = os.path.join("venv", "bin", "pip3")

subprocess.run([pip_path, "install", "-r", "requirements.txt"])