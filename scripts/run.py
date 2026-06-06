import subprocess

subprocess.run(["python", "scripts/fetch_jobs.py"])

subprocess.run(["python", "scripts/dedupe.py"])

subprocess.run(["python", "scripts/generate_csv.py"])

subprocess.run(["python", "scripts/generate_html.py"])