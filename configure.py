import subprocess
import os

subprocess.run(["python", "-m", "virtualenv", "venv"])
subprocess.run([os.path.join("venv", "Scripts", "pip3"), "install", "-r", "requirements.txt"])