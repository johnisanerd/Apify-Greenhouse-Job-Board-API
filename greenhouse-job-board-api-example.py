"""Greenhouse Job Board API: example client.

Pulls live jobs from any Greenhouse-hosted career site, discovers companies
hiring through Greenhouse, and tracks new or changed postings. No Harvest
key and no login: give it board tokens or URLs, or nothing at all and let it
sweep its bundled company directory.

Get a free Apify API token: https://apify.com?fpr=9n7kx3
Actor: https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3

Run it:
    uv sync
    cp .env.example .env      # then paste your token into .env
    uv run python greenhouse-job-board-api-example.py

Pick one example:
    uv run python greenhouse-job-board-api-example.py --example jobs
    uv run python greenhouse-job-board-api-example.py --example companies
    uv run python greenhouse-job-board-api-example.py --example new-jobs
    uv run python greenhouse-job-board-api-example.py --example markdown
    uv run python greenhouse-job-board-api-example.py --example salary
    uv run python greenhouse-job-board-api-example.py --example all
"""

import argparse
import os
import sys

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/greenhouse-job-board-api"

# Every run below asks for a small number of rows on purpose. You pay per row
# delivered, so keep the first run cheap, confirm the shape of the data, then
# raise maxJobs once you know it is what you want.
SMALL = 10


def client() -> ApifyClient:
    token = os.getenv("APIFY_TOKEN")
    if not token or token == "your_apify_api_token_here":
        sys.exit(
            "Set APIFY_TOKEN first. Copy .env.example to .env and paste your token.\n"
            "Get one free: https://apify.com?fpr=9n7kx3"
        )
    return ApifyClient(token)


def rows(api: ApifyClient, run_input: dict, limit: int = 5) -> list[dict]:
    """Run the Actor and return the first rows of its dataset.

    apify-client 3.x returns a typed Run object here, not a dict, so the
    dataset id is an attribute. On 2.x this was run["defaultDatasetId"].
    """
    run = api.actor(ACTOR_ID).call(run_input=run_input)
    return list(api.dataset(run.default_dataset_id).iterate_items(limit=limit))


def run_jobs(api: ApifyClient) -> None:
    """Full job records from named boards, filtered before billing.

    Mirrors the "Use the Greenhouse Job Board API Without a Key" task. Title
    and location filters run before anything is charged, so filtered jobs
    cost nothing.
    """
    print("\n=== Full job records ===")
    results = rows(api, {
        "companies": ["gitlab", "stripe"],
        "titleKeywords": ["engineer"],
        "maxJobs": SMALL,
    })
    for job in results:
        location = job.get("location") or "location not stated"
        remote = " [remote]" if job.get("isRemote") else ""
        print(f"\n{job.get('title')}{remote}")
        print(f"  {job.get('companyName')} | {location}")
        print(f"  published {str(job.get('datePublished'))[:10]} | updated {str(job.get('dateUpdated'))[:10]}")
        print(f"  apply: {job.get('url')}")
        description = job.get("descriptionMarkdown") or ""
        if description:
            print(f"  {description[:140].strip()}...")


def run_companies(api: ApifyClient) -> None:
    """Discover companies hiring through Greenhouse, live-verified.

    Mirrors the "Find Companies Using Greenhouse ATS" task. Each row carries a
    current open-jobs count; dead boards are skipped and never billed.
    """
    print("\n=== Companies hiring through Greenhouse ===")
    results = rows(api, {
        "outputMode": "companiesOnly",
        "maxCompanies": SMALL,
        "maxJobs": SMALL,
    }, limit=SMALL)
    for company in results:
        print(f"{company.get('boardToken'):<28} {str(company.get('jobCount')):>5} open  {company.get('boardUrl')}")


def run_new_jobs(api: ApifyClient) -> None:
    """Only jobs updated in the last week, with zero state to manage.

    Mirrors the "Track New Greenhouse Job Postings Daily" task. The cutoff
    compares against the employer's own updated_at timestamp, so a daily
    schedule with updatedAfter set to 25h becomes a change feed.
    """
    print("\n=== Jobs updated in the last 7 days ===")
    results = rows(api, {
        "companies": ["gitlab"],
        "updatedAfter": "7d",
        "maxJobs": SMALL,
    }, limit=SMALL)
    if not results:
        print("No postings updated in the window. Widen updatedAfter and rerun.")
    for job in results:
        print(f"{str(job.get('dateUpdated'))[:10]}  {job.get('title')}  ({job.get('companyName')})")


def run_markdown(api: ApifyClient) -> None:
    """Descriptions as clean Markdown, ready for an LLM.

    Mirrors the "Greenhouse Jobs as Markdown for AI Agents" task. Markdown is
    the default format; hand the rows straight to a model without stripping
    HTML first.
    """
    print("\n=== Markdown descriptions for AI pipelines ===")
    results = rows(api, {
        "companies": ["anthropic"],
        "includeDescriptionMarkdown": True,
        "maxJobs": 3,
    }, limit=3)
    for job in results:
        print(f"\n## {job.get('title')} ({job.get('companyName')})")
        print((job.get("descriptionMarkdown") or "")[:300].strip(), "...")


def run_salary(api: ApifyClient) -> None:
    """Postings with compensation: published pay ranges plus parsed salaries.

    Mirrors the "Greenhouse Job Postings With Salary Data" task. salaryRaw is
    the board's own structured pay range when published; salaryDerived is
    parsed from the description text with currency and period.
    """
    print("\n=== Jobs with salary data ===")
    results = rows(api, {
        "companies": ["gitlab", "carvana"],
        "includeDescriptionText": True,
        "maxJobs": 20,
    }, limit=20)
    for job in results:
        salary = job.get("salaryDerived") or job.get("salaryRaw")
        if not salary:
            continue
        if isinstance(salary, dict) and "min" in salary:
            band = f"{salary.get('currency') or ''} {salary.get('min'):,.0f} - {salary.get('max'):,.0f} per {salary.get('period')}"
        else:
            band = str(salary)[:60]
        print(f"{job.get('title')[:48]:<50} {band}")


EXAMPLES = {
    "jobs": run_jobs,
    "companies": run_companies,
    "new-jobs": run_new_jobs,
    "markdown": run_markdown,
    "salary": run_salary,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Greenhouse Job Board API examples")
    parser.add_argument("--example", choices=[*EXAMPLES, "all"], default="jobs",
                        help="Which example to run (default: jobs)")
    args = parser.parse_args()

    api = client()
    chosen = list(EXAMPLES) if args.example == "all" else [args.example]
    for name in chosen:
        EXAMPLES[name](api)


if __name__ == "__main__":
    main()
