import requests
import os

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")

ACTORS = [
    {
        "name": "linkedin_1",
        "id": "PeTP8M7vkdTthJvqk",
        "input": {
            "mode": "jobs",
            "searchQuery": "Salesforce Developer",
            "location": "Canada",
            "maxResults": 50
        }
    },
    {
        "name": "linkedin_2",
        "id": "zn01OAlzP853oqn4Z",
        "input": {
            "mode": "jobs",
            "searchQuery": "Salesforce Administrator",
            "location": "Canada",
            "maxResults": 50
        }
    },
    {
        "name": "indeed",
        "id": "MXLpngmVpE8WTESQr",
        "input": {
            "query": "Salesforce Developer",
            "location": "Canada",
            "maxResults": 50
        }
    }
]

def run_actor(actor_id, payload):
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={APIFY_TOKEN}"
    r = requests.post(url, json=payload)
    return r.json()

all_jobs = []

for actor in ACTORS:
    try:
        data = run_actor(actor["id"], actor["input"])

        for j in data:
            all_jobs.append({
                "company": j.get("company") or j.get("companyName"),
                "title": j.get("title") or j.get("position"),
                "location": j.get("location"),
                "url": j.get("url") or j.get("jobUrl"),
                "salary": j.get("salary"),
                "source": actor["name"],
                "description": j.get("description")
            })

    except Exception as e:
        print(f"Error in {actor['name']}: {e}")

import json
with open("output/raw_jobs.json", "w") as f:
    json.dump(all_jobs, f, indent=2)

print("Jobs collected:", len(all_jobs))