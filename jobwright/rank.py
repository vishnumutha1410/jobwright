"""Score and rank jobs against the candidate profile.

Composite score (0-100) = weighted blend of skills overlap, location preference,
posting recency, and whether a salary is listed. Also generates the human-facing
'why I match' / 'skill gaps' summaries.
"""
from config import CANDIDATE, PREFERRED_LOCATIONS, WEIGHTS, PRIORITY_THRESHOLDS, MAX_POSTING_AGE_DAYS


def _skill_overlap(job) -> tuple[float, list, list]:
    core = set(s.lower() for s in CANDIDATE["core_skills"])
    req = [s for s in job.req_skills]
    if not req:
        return 0.5, [], []
    matched = [s for s in req if s.lower() in core or any(c in s.lower() for c in core)]
    missing = [s for s in req if s not in matched]
    return len(matched) / len(req), matched, missing


def _location_score(job) -> float:
    loc = job.location.lower()
    return 1.0 if any(p in loc for p in PREFERRED_LOCATIONS) else 0.4


def _recency_score(job) -> float:
    # 0 days -> 1.0, MAX_POSTING_AGE_DAYS -> ~0.3
    d = min(job.posted_days_ago, MAX_POSTING_AGE_DAYS)
    return max(0.3, 1.0 - (d / MAX_POSTING_AGE_DAYS) * 0.7)


def _salary_score(job) -> float:
    return 1.0 if job.salary else 0.5


def score(job) -> object:
    overlap, matched, missing = _skill_overlap(job)
    raw = (
        WEIGHTS["skills"] * overlap
        + WEIGHTS["location"] * _location_score(job)
        + WEIGHTS["recency"] * _recency_score(job)
        + WEIGHTS["salary"] * _salary_score(job)
    )
    job.match_score = round(raw * 100)
    job.priority = (
        "High" if job.match_score >= PRIORITY_THRESHOLDS["High"]
        else "Medium" if job.match_score >= PRIORITY_THRESHOLDS["Medium"]
        else "Low"
    )
    job.why_match = (
        f"Overlaps on {', '.join(matched) or 'core data-engineering fundamentals'}; "
        f"posted {job.posted_days_ago}d ago; "
        f"{'preferred location' if _location_score(job) > 0.5 else 'US-based'}."
    )
    job.skill_gaps = ", ".join(missing) if missing else "No obvious gaps from the listing."
    return job


def rank(jobs: list) -> list:
    """Filter to fresh, entry-level roles then sort by score (desc)."""
    fresh = [j for j in jobs if j.posted_days_ago <= MAX_POSTING_AGE_DAYS]
    for j in fresh:
        score(j)
    return sorted(fresh, key=lambda j: j.match_score, reverse=True)
