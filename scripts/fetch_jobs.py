import json
import os
from pathlib import Path

from jobspy import scrape_jobs


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

DEFAULT_JOB_SITES = ["indeed", "linkedin", "glassdoor"]


def env_list(name, default):
    value = os.getenv(name)
    if not value:
        return default

    return [item.strip() for item in value.split(",") if item.strip()]


def country_for_location(location):
    countries_by_location = {
        "united states": "USA",
        "us": "USA",
        "usa": "USA",
        "remote us": "USA",
        "remote usa": "USA",
        "canada": "Canada",
        "remote": "Canada",
        "remote canada": "Canada",
        "toronto": "Canada",
        "ottawa": "Canada",
        "montreal": "Canada",
    }

    return countries_by_location.get(
        location.strip().lower(),
        os.getenv("JOB_COUNTRY", "Canada"),
    )


def is_remote_location(location):
    return "remote" in location.strip().lower()


def clean_value(value):
    if value is None:
        return None

    try:
        if value != value:
            return None
    except TypeError:
        pass

    return value


def build_salary(row):
    interval = clean_value(row.get("interval"))
    currency = clean_value(row.get("currency"))
    min_amount = clean_value(row.get("min_amount"))
    max_amount = clean_value(row.get("max_amount"))

    parts = []
    if min_amount and max_amount:
        parts.append(f"{min_amount}-{max_amount}")
    elif min_amount:
        parts.append(str(min_amount))
    elif max_amount:
        parts.append(str(max_amount))

    if currency:
        parts.append(str(currency))
    if interval:
        parts.append(str(interval))

    return " ".join(parts) if parts else None


def build_location(row):
    location = clean_value(row.get("location"))
    if location:
        return location

    parts = [
        clean_value(row.get("city")),
        clean_value(row.get("state")),
        clean_value(row.get("country")),
    ]
    return ", ".join(str(part) for part in parts if part) or None


def normalize_job(row, query, location):
    return {
        "company": clean_value(row.get("company")) or clean_value(row.get("company_name")),
        "title": clean_value(row.get("title")),
        "location": build_location(row),
        "url": clean_value(row.get("job_url")) or clean_value(row.get("url")),
        "salary": build_salary(row),
        "source": clean_value(row.get("site")) or clean_value(row.get("source")),
        "description": clean_value(row.get("description")),
        "search_query": query,
        "search_location": location,
        "date_posted": str(clean_value(row.get("date_posted")) or ""),
        "is_remote": bool(clean_value(row.get("is_remote"))),
    }


def scrape_search(query, location, sites, results_wanted, hours_old):
    kwargs = {
        "site_name": sites,
        "search_term": query,
        "location": location,
        "results_wanted": results_wanted,
        "country_indeed": country_for_location(location),
        "is_remote": is_remote_location(location),
    }

    if hours_old:
        kwargs["hours_old"] = hours_old

    print(f"Searching {sites} for {query!r} in {location!r}")
    return scrape_jobs(**kwargs)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    queries = env_list("JOB_QUERIES", DEFAULT_JOB_QUERIES)
    locations = env_list("JOB_LOCATIONS", DEFAULT_JOB_LOCATIONS)
    sites = env_list("JOB_SITES", DEFAULT_JOB_SITES)
    results_wanted = int(os.getenv("JOB_RESULTS_WANTED", os.getenv("APIFY_JOB_COUNT", "25")))
    hours_old = os.getenv("JOB_HOURS_OLD")
    hours_old = int(hours_old) if hours_old else None

    all_jobs = []
    errors = []

    for query in queries:
        for location in locations:
            try:
                jobs = scrape_search(query, location, sites, results_wanted, hours_old)
                print(f"Found {len(jobs)} raw jobs for {query!r} in {location!r}")

                for row in jobs.to_dict("records"):
                    job = normalize_job(row, query, location)
                    if job["title"] or job["company"] or job["url"]:
                        all_jobs.append(job)

            except Exception as exc:
                message = f"{query} / {location}: {exc}"
                print(f"Error: {message}")
                errors.append(message)

    with RAW_JOBS_PATH.open("w", encoding="utf-8") as file:
        json.dump(all_jobs, file, indent=2)

    print("Jobs collected:", len(all_jobs))

    if errors and not all_jobs:
        raise RuntimeError("All job searches failed: " + "; ".join(errors))

    if errors:
        print("Some searches failed:")
        for error in errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()
