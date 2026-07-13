"""Discover job listings from open Built In boards, resolve direct apply URLs,
and read each posting's real age + active status from its detail page.

Anchor-driven list parsing (robust to markup changes). For each job we open the
detail page once to (a) get the direct company/ATS apply link, (b) read the
"Posted X Days Ago" date reliably, and (c) skip roles that were removed/closed.
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
_SALARY_RE = re.compile(r"\$?\d{2,3}K\s*[-â€“]\s*\$?\d{2,3}K", re.I)
_LOC_RE = re.compile(r"(Remote|Austin|Dallas|Houston|San Antonio|[A-Z][a-z]+,\s*[A-Z]{2})")
_DEAD = ("was removed", "no longer accepting", "no longer available", "this job has expired")
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


def _skills(text):
    low, found = text.lower(), []
    for s in _SKILL_VOCAB:
        if s.lower() in low and s not in found:
            found.append(s)
    return found


def _card_container(anchor):
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
            posted_days_ago=_age_days(text),
            listing_url=href,
            req_skills=_skills(text),
        ))
    return jobs


def parse_detail(html):
    """Return (apply_url_or_None, age_days, active) from a Built In job page."""
    soup = BeautifulSoup(html, "html.parser")
    full = soup.get_text(" ", strip=True)
    head = full[:2500]                       # the header region, before 'Similar Jobs'
    if any(d in head.lower() for d in _DEAD):
        return None, 999, False, ""
    # cut off before the similar-jobs / description noise so we read the real post date
    for marker in ("Read Full Description", "Similar Jobs", "What We Do"):
        i = head.find(marker)
        if i != -1:
            head = head[:i]
            break
    age = _age_days(head)
    apply_url = None
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "apply" and any(h in a["href"].lower() for h in _ATS_HINTS):
            apply_url = a["href"]
            break
    if not apply_url:
        for a in soup.find_all("a", href=True):
            if any(h in a["href"].lower() for h in _ATS_HINTS):
                apply_url = a["href"]
                break
    company = ""
    c = soup.find("a", href=re.compile(r"/company/"))
    if c and c.get_text(strip=True):
        company = c.get_text(strip=True)
    return apply_url, age, True, company


def discover():
    """Search boards, dedupe, then read real age + active status from each detail page."""
    seen, out = set(), []
    for board in SOURCE_BOARDS:
        for job in parse_board(board):
            if job.job_id in seen:
                continue
            seen.add(job.job_id)
            html = _get(job.listing_url)
            if html:
                apply_url, age, active, company = parse_detail(html)
                if not active:
                    continue                 # skip removed/closed roles
                job.apply_url = apply_url or job.listing_url
                if company:
                    job.company = company
                if age < 900:
                    job.posted_days_ago = age
            else:
                job.apply_url = job.listing_url
            out.append(job)
    return out
