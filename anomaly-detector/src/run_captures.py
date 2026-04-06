###
# Run this program to start both PLC and Network captures simultaneously.
# Make sure to have the PLC simulator running before starting this.
# Press Ctrl+C to stop both captures when done.
###

from pathlib import Path
import subprocess
import time
import sys

BASE = Path(__file__).resolve().parent

processes = []

try:
  print("Starting network capture...")
  p1 = subprocess.Popen([sys.executable, str(BASE / "main.py")])
  processes.append(p1)

  time.sleep(1)

  print("Starting PLC data capture...")
  p2 = subprocess.Popen([sys.executable, str(BASE / "modbus_client.py")])
  processes.append(p2)

  print("All captures started. Press Ctrl+C to stop.")

  while True:
    time.sleep(1)

except KeyboardInterrupt:
  print("\nStopping captures...")
  for p in processes:
    p.terminate()
  print("All captures stopped.")
