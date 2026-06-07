import subprocess
import sys

subprocess.run([sys.executable, "scripts/fetch_apify.py"], check=True)
subprocess.run([sys.executable, "scripts/dedupe.py"], check=True)
subprocess.run([sys.executable, "scripts/export.py"], check=True)
