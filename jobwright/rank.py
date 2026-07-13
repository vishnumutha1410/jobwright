"""Score and rank jobs against the candidate profile.

Composite score (0-100) = weighted blend of skills overlap, location preference,
posting recency, and salary signal. STRICT freshness: only roles posted within
MAX_POSTING_AGE_DAYS (default 7) are kept - ages come reliably from each job's
detail page (see search.parse_detail). Results are filtered by a minimum score
and capped so you get a focused batch.
"""
from config import CANDIDATE, PREFERRED_LOCATIONS, WEIGHTS, PRIORITY_THRESHOLDS, MAX_POSTING_AGE_DAYS

DEFAULT_LIMIT = 15
DEFAULT_MIN_SCORE = 50


def _skill_overlap(job):
    core = set(s.lower() for s in CANDIDATE["core_skills"])
    req = [s for s in job.req_skills]
    if not req:
        return 0.5, [], []
    matched = [s for s in req if s.lower() in core or any(c in s.lower() for c in core)]
    missing = [s for s in req if s not in matched]
    return len(matched) / len(req), matched, missing


def _location_score(job):
    return 1.0 if any(p in job.location.lower() for p in PREFERRED_LOCATIONS) else 0.4


def _recency_score(job):
    d = min(job.posted_days_ago, MAX_POSTING_AGE_DAYS)
    return max(0.3, 1.0 - (d / MAX_POSTING_AGE_DAYS) * 0.7)


def _salary_score(job):
    return 1.0 if job.salary else 0.5


def score(job):
    overlap, matched, missing = _skill_overlap(job)
    raw = (WEIGHTS["skills"] * overlap + WEIGHTS["location"] * _location_score(job)
           + WEIGHTS["recency"] * _recency_score(job) + WEIGHTS["salary"] * _salary_score(job))
    job.match_score = round(raw * 100)
    job.priority = ("High" if job.match_score >= PRIORITY_THRESHOLDS["High"]
                    else "Medium" if job.match_score >= PRIORITY_THRESHOLDS["Medium"] else "Low")
    job.why_match = ("Overlaps on " + (", ".join(matched) or "core data-engineering fundamentals")
                     + "; posted " + str(job.posted_days_ago) + "d ago; "
                     + ("preferred location" if _location_score(job) > 0.5 else "US-based") + ".")
    job.skill_gaps = ", ".join(missing) if missing else "No obvious gaps from the listing."
    return job


def rank(jobs, limit=DEFAULT_LIMIT, min_score=DEFAULT_MIN_SCORE):
    """Keep only roles posted within the last MAX_POSTING_AGE_DAYS, score, filter, cap."""
    fresh = [j for j in jobs if j.posted_days_ago <= MAX_POSTING_AGE_DAYS]
    for j in fresh:
        score(j)
    fresh = [j for j in fresh if j.match_score >= min_score]
    fresh.sort(key=lambda j: j.match_score, reverse=True)
    return fresh[:limit]
