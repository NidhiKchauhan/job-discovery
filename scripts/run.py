import subprocess
import sys

subprocess.run([sys.executable, "scripts/fetch_jobs.py"], check=True)
subprocess.run([sys.executable, "scripts/dedupe.py"], check=True)
subprocess.run([sys.executable, "scripts/export.py"], check=True)
