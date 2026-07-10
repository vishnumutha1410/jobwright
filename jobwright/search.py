"""Discover job listings from open Built In boards and resolve direct apply URLs.

Built In job boards are publicly indexed and expose the real company/ATS apply
link behind each posting's "Apply" button, which we extract so the user lands on
the actual application page rather than an aggregator.
"""
import re
import time
import requests
from bs4 import BeautifulSoup

from config import SOURCE_BOARDS, TARGET_TITLES, ENTRY_SIGNALS
from .models import Job

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Jobwright/1.0; +portfolio-project)"}
_AGE_RE = re.compile(r"(\d+)\s+day", re.I)
# Known ATS / careers domains we treat as a valid "direct apply" destination.
_ATS_HINTS = (
    "greenhouse.io", "ashbyhq.com", "lever.co", "myworkdayjobs.com",
    "smartrecruiters.com", "oraclecloud.com", "icims.com", "bamboohr.com",
    "jobvite.com", "workable.com", "careers", "/apply",
)


def _get(url, tries=3, pause=1.5):
    for i in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.ok:
                return r.text
        except requests.RequestException:
            pass
        time.sleep(pause * (i + 1))
    return ""


def _parse_age_days(text: str) -> int:
    text = text.lower()
    if "yesterday" in text or "hour" in text or "minute" in text:
        return 1
    m = _AGE_RE.search(text)
    return int(m.group(1)) if m else 999


def _looks_entry(text: str) -> bool:
    t = text.lower()
    return any(sig in t for sig in ENTRY_SIGNALS)


def _title_matches(title: str) -> bool:
    t = title.lower()
    return any(tt in t for tt in TARGET_TITLES)


def resolve_apply_url(listing_url: str) -> str:
    """Open a Built In job page and return the external apply link if present."""
    html = _get(listing_url)
    if not html:
        return listing_url
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "apply":
            href = a["href"]
            if any(h in href.lower() for h in _ATS_HINTS):
                return href
    # Fallback: any external ATS-looking link on the page.
    for a in soup.find_all("a", href=True):
        if any(h in a["href"].lower() for h in _ATS_HINTS):
            return a["href"]
    return listing_url


def parse_board(board_url: str) -> list[Job]:
    """Extract job cards from a Built In board page."""
    html = _get(board_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("[data-id='job-card'], div.job-item, article"):
        link = card.find("a", href=re.compile(r"/job/"))
        if not link:
            continue
        title = link.get_text(strip=True)
        if not _title_matches(title):
            continue
        company_el = card.find("a", href=re.compile(r"/company/"))
        card_text = card.get_text(" ", strip=True)
        job = Job(
            company=company_el.get_text(strip=True) if company_el else "Unknown",
            title=title,
            location=_first_location(card_text),
            salary=_first_salary(card_text),
            experience="Entry level" if _looks_entry(card_text) else "",
            posted_days_ago=_parse_age_days(card_text),
            listing_url=_abs(board_url, link["href"]),
            req_skills=_extract_skills(card_text),
        )
        jobs.append(job)
    return jobs


def _abs(base, href):
    if href.startswith("http"):
        return href
    root = "/".join(base.split("/")[:3])
    return root + href


_SALARY_RE = re.compile(r"\$?\d{2,3}K\s*[-–]\s*\$?\d{2,3}K", re.I)
_LOC_RE = re.compile(r"(Remote|Austin|Dallas|Houston|San Antonio|[A-Z][a-z]+,\s*[A-Z]{2})")


def _first_salary(text):
    m = _SALARY_RE.search(text)
    return m.group(0) if m else ""


def _first_location(text):
    m = _LOC_RE.search(text)
    return m.group(0) if m else ""


_SKILL_VOCAB = [
    "SQL", "Python", "Snowflake", "dbt", "Airflow", "PySpark", "Spark", "Docker",
    "AWS", "Azure", "GCP", "Pandas", "NumPy", "PostgreSQL", "Postgres", "ETL",
    "ELT", "Databricks", "Iceberg", "Kafka", "Power BI", "Tableau", "Redshift",
    "BigQuery", "Terraform", "Git", "Java", "Scala",
]


def _extract_skills(text):
    found = []
    low = text.lower()
    for s in _SKILL_VOCAB:
        if s.lower() in low and s not in found:
            found.append(s)
    return found


def discover() -> list[Job]:
    """Search all configured boards and de-duplicate by job_id."""
    seen, out = set(), []
    for board in SOURCE_BOARDS:
        for job in parse_board(board):
            if job.job_id in seen:
                continue
            seen.add(job.job_id)
            job.apply_url = resolve_apply_url(job.listing_url)
            out.append(job)
    return out
