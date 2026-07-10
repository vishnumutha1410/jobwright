"""End-to-end run: discover -> dedupe -> rank -> compose -> draft -> persist."""
import logging

from . import search, rank, compose, tracker
from .gmail_drafts import create_draft

log = logging.getLogger("jobwright")


def run(dry_run: bool = False) -> list:
    """Execute one full pipeline pass. Returns the list of NEW jobs processed."""
    log.info("Discovering listings...")
    found = search.discover()
    log.info("Found %d listings", len(found))

    already = tracker.seen_ids()
    new_jobs = [j for j in found if j.job_id not in already]
    log.info("%d are new after dedupe", len(new_jobs))

    ranked = rank.rank(new_jobs)          # filters to fresh + entry-level, sorts by score
    for job in ranked:
        compose.enrich(job)               # note + interview tips
        if not dry_run:
            subject = f"Application - {job.title} at {job.company} ({job.match_score}% match, ACTIVE)"
            try:
                create_draft(subject, compose.email_body(job))
            except Exception as e:          # keep going even if one draft fails
                log.warning("Draft failed for %s: %s", job.company, e)

    if ranked and not dry_run:
        tracker.append_jobs(ranked)

    _notify(ranked)
    return ranked


def _notify(jobs):
    if not jobs:
        log.info("No new matching jobs this run.")
        return
    print("\n=== New opportunities ===")
    for j in jobs:
        print(f"[{j.priority}] {j.match_score}%  {j.company} — {j.title}  ({j.posted_days_ago}d)")
        print(f"         apply: {j.apply_url}")
