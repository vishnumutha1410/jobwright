"""Discover job listings from open Built In boards and resolve direct apply URLs.

Robust, anchor-driven parser: instead of depending on fragile CSS class names,
it finds every /job/<slug>/<id> link and reads the surrounding card text. This
survives Built In markup changes far better than class selectors.
"""
import re
import time
import requests
from bs4 import BeautifulSoup

from config import SOURCE_BOARDS, TARGET_TITLES, ENTRY_SIGNALS
from .models import Job

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Jobwright/1.0; +portfolio-project)"}
_JOB_HREF = re.compile(r"/job/[^/\"']+/\d+")
_AGE_RE = re.compile(r"(\d+)\s+day", re.I)
_SALARY_RE = re.compile(r"\$?\d{2,3}K\s*[-\u2013]\s*\$?\d{2,3}K", re.I)
_LOC_RE = re.compile(r"(Remote|Austin|Dallas|Houston|San Antonio|[A-Z][a-z]+,\s*[A-Z]{2})")
_ATS_HINTS = (
    "greenhouse.io", "ashbyhq.com", "lever.co", "myworkdayjobs.com",
    "smartrecruiters.com", "oraclecloud.com", "icims.com", "bamboohr.com",
    "jobvite.com", "workable.com", "fglife.com", "/careers", "/apply",
)
_SKILL_VOCAB = [
    "SQL", "Python", "Snowflake", "dbt", "Airflow", "PySpark", "Spark", "Docker",
    "AWS", "Azure", "GCP", "Pandas", "NumPy", "PostgreSQL", "Postgres", "ETL",
    "ELT", "Databricks", "Iceberg", "Kafka", "Power BI", "Tableau", "Redshift",
    "BigQuery", "Terraform", "Git", "Java", "Scala",
]


def _get(url, tries=3, pause=1.5):
    for i in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.ok:
                return r.text
        except requests.RequestException:
            pass
        time.sleep(pause * (i + 1))
    return ""


def _abs(base, href):
    if href.startswith("http"):
        return href
    return "/".join(base.split("/")[:3]) + href


def _age_days(text):
    t = text.lower()
    if "yesterday" in t or "hour" in t or "minute" in t or "today" in t:
        return 1
    m = _AGE_RE.search(t)
    return int(m.group(1)) if m else 999


def _title_matches(title):
    t = title.lower()
    return any(tt in t for tt in TARGET_TITLES)


def _entry(text):
    t = text.lower()
    return any(sig in t for sig in ENTRY_SIGNALS)


def _skills(text):
    low, found = text.lower(), []
    for s in _SKILL_VOCAB:
        if s.lower() in low and s not in found:
            found.append(s)
    return found


def _card_container(anchor):
    """Walk up until we find the ancestor that also holds a /company/ link."""
    node = anchor
    for _ in range(6):
        node = node.parent
        if node is None:
            break
        if node.find("a", href=re.compile(r"/company/")):
            return node
    return anchor.parent or anchor


def parse_board(board_url):
    html = _get(board_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    jobs, seen = [], set()
    for a in soup.find_all("a", href=_JOB_HREF):
        title = a.get_text(strip=True)
        if not title or not _title_matches(title):
            continue
        href = _abs(board_url, a["href"])
        if href in seen:
            continue
        seen.add(href)
        box = _card_container(a)
        text = box.get_text(" ", strip=True)
        comp = box.find("a", href=re.compile(r"/company/"))
        sal = _SALARY_RE.search(text)
        loc = _LOC_RE.search(text)
        jobs.append(Job(
            company=comp.get_text(strip=True) if comp else "Unknown",
            title=title,
            location=loc.group(0) if loc else "",
            salary=sal.group(0) if sal else "",
            experience="Entry level" if _entry(text) else "",
            posted_days_ago=_age_days(text),
            listing_url=href,
            req_skills=_skills(text),
        ))
    return jobs


def resolve_apply_url(listing_url):
    """Open a Built In job page and return the external ATS/apply link if present."""
    html = _get(listing_url)
    if not html:
        return listing_url
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "apply" and any(h in a["href"].lower() for h in _ATS_HINTS):
            return a["href"]
    for a in soup.find_all("a", href=True):
        if any(h in a["href"].lower() for h in _ATS_HINTS):
            return a["href"]
    return listing_url


def discover():
    """Search all configured boards, dedupe by job_id, resolve direct apply URLs."""
    seen, out = set(), []
    for board in SOURCE_BOARDS:
        for job in parse_board(board):
            if job.job_id in seen:
                continue
            seen.add(job.job_id)
            job.apply_url = resolve_apply_url(job.listing_url)
            out.append(job)
    return out
