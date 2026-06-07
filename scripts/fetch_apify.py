import json
import os
from pathlib import Path

import requests


APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")

OUTPUT_DIR = Path("output")
RAW_JOBS_PATH = OUTPUT_DIR / "raw_jobs.json"

DEFAULT_JOB_QUERIES = [
    "Salesforce Developer",
    "Salesforce Administrator",
    "Salesforce Consultant",
    "Salesforce Business Analyst",
    "Salesforce Specialist",
    "Salesforce CPQ",
    "Salesforce AI Developer",
    "Salesforce System",
]

DEFAULT_JOB_LOCATIONS = [
    "Canada",
    "United States",
    "Remote Canada",
    "Remote US",
    "Toronto",
    "Ottawa",
    "Montreal",
]


def env_list(name, default):
    value = os.getenv(name)
    if not value:
        return default

    return [item.strip() for item in value.split(",") if item.strip()]


def country_for_location(location):
    countries_by_location = {
        "united states": "us",
        "us": "us",
        "usa": "us",
        "canada": "ca",
        "remote": "ca",
        "remote canada": "ca",
        "remote us": "us",
        "remote usa": "us",
        "toronto": "ca",
        "ottawa": "ca",
        "montreal": "ca",
    }

    return countries_by_location.get(
        location.strip().lower(),
        os.getenv("APIFY_INDEED_COUNTRY", "ca"),
    )


def build_actor_runs():
    queries = env_list("APIFY_JOB_QUERIES", DEFAULT_JOB_QUERIES)
    locations = env_list("APIFY_JOB_LOCATIONS", DEFAULT_JOB_LOCATIONS)
    count = int(os.getenv("APIFY_JOB_COUNT", "50"))

    runs = []
    for query in queries:
        for location in locations:
            runs.append(
                {
                    "name": f"indeed:{query}:{location}",
                    # REST API actor ids use "~"; the Python client accepts "curious_coder/indeed-scraper".
                    "id": "curious_coder~indeed-scraper",
                    "input": {
                        "country": country_for_location(location),
                        "query": query,
                        "location": location,
                        "count": count,
                    },
                }
            )

    return runs


def run_actor(actor_id, payload):
    if not APIFY_TOKEN:
        raise RuntimeError("APIFY_API_TOKEN is not set")

    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    response = requests.post(url, params={"token": APIFY_TOKEN}, json=payload, timeout=180)

    if response.status_code >= 400:
        raise RuntimeError(
            f"Apify returned HTTP {response.status_code}: {response.text[:500]}"
        )

    data = response.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Expected a list of dataset items, got: {data}")

    return data


def normalize_job(item, source):
    company_details = item.get("companyDetails") or {}
    salary = item.get("salary") or item.get("extractedSalary")

    if isinstance(salary, dict):
        salary = salary.get("text") or " ".join(
            str(part)
            for part in [
                salary.get("min"),
                salary.get("max"),
                salary.get("currencyCode"),
                salary.get("type"),
            ]
            if part
        )

    return {
        "company": item.get("company") or item.get("companyName") or company_details.get("name"),
        "title": item.get("title") or item.get("displayTitle") or item.get("position"),
        "location": item.get("location") or item.get("formattedLocation"),
        "url": item.get("url") or item.get("jobUrl") or item.get("thirdPartyApplyUrl"),
        "salary": salary,
        "source": source,
        "description": item.get("description") or item.get("jobDescription"),
    }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    all_jobs = []
    errors = []

    for actor in build_actor_runs():
        try:
            print(f"Running {actor['name']} with input: {actor['input']}")
            data = run_actor(actor["id"], actor["input"])
            print(f"{actor['name']} returned {len(data)} raw items")

            for item in data:
                job = normalize_job(item, actor["name"])
                if job["title"] or job["company"] or job["url"]:
                    all_jobs.append(job)

        except Exception as exc:
            print(f"Error in {actor['name']}: {exc}")
            errors.append(f"{actor['name']}: {exc}")

    with RAW_JOBS_PATH.open("w", encoding="utf-8") as file:
        json.dump(all_jobs, file, indent=2)

    print("Jobs collected:", len(all_jobs))

    if errors:
        raise RuntimeError("Apify fetch failed: " + "; ".join(errors))


if __name__ == "__main__":
    main()
