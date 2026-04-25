import os
import sys
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"
REQ_FILE = PROJECT_DIR / "requirements.txt"

def run(cmd):
    print("==>", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)

def venv_python():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def main():
    print("==> Creating virtual environment...")
    run([sys.executable, "-m", "venv", str(VENV_DIR)])

    py = venv_python()

    print("==> Upgrading pip...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    if REQ_FILE.exists():
        print("==> Installing requirements...")
        run([str(py), "-m", "pip", "install", "-r", str(REQ_FILE)])
    else:
        print("WARNING: requirements.txt not found.")

    print("\nSetup complete.")
    if os.name == "nt":
        print("Activate with:")
        print(r"  .venv\Scripts\Activate.ps1")
    else:
        print("Activate with:")
        print("  source .venv/bin/activate")

    print("\nRun with:")
    print("  python app.py")

if __name__ == "__main__":
    main()