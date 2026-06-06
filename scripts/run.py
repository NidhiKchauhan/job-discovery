import subprocess

subprocess.run(["python", "scripts/fetch_apify.py"])
subprocess.run(["python", "scripts/dedupe.py"])
subprocess.run(["python", "scripts/export.py"])