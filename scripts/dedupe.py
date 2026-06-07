import json

with open("output/raw_jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

seen = set()
unique_jobs = []

for job in jobs:
    key = (
        (job.get("company") or "").strip().lower(),
        (job.get("title") or "").strip().lower(),
        (job.get("url") or "").strip().lower(),
    )

    if key not in seen:
        seen.add(key)
        unique_jobs.append(job)

with open("output/jobs.json", "w", encoding="utf-8") as f:
    json.dump(unique_jobs, f, indent=2)

print(f"Unique jobs: {len(unique_jobs)}")
