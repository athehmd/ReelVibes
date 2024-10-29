import subprocess

subprocess.run(["python", "-m", "virtualenv", "venv"])
subprocess.run(["venv\scripts\activate"])
subprocess.run(["pip3", "install", "-r", "requirements.txt"])