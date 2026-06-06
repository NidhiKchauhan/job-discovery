import json
import pandas as pd

jobs = json.load(open("output/jobs.json"))

df = pd.DataFrame(jobs)

df.to_csv("output/jobs.csv", index=False)

df.to_html("output/jobs.html", index=False)

print("Export done")