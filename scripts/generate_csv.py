import json
import pandas as pd

with open("output/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

df = pd.DataFrame(jobs)

df.to_csv(
    "output/jobs.csv",
    index=False
)

print("CSV generated")