"""Cloud entry point: discover -> dedupe -> rank -> email a digest of NEW jobs.

Self-contained for GitHub Actions (headless). Emails via Gmail SMTP using an app
password from env vars, remembers seen jobs in seen.json (committed back by the
workflow), and alerts if a scan returns nothing so it can't go silent.
Env: MAIL_USERNAME, MAIL_APP_PASSWORD, MAIL_TO (optional).
"""
import os
import ssl
import json
import smtplib
import logging
from email.mime.text import MIMEText

from jobwright import search, rank, compose

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("jobwright")
SEEN_PATH = "seen.json"

CARD = (
    '<div style="border:1px solid #ddd;border-radius:10px;padding:14px 16px;margin:0 0 12px">'
    '<div style="font-size:16px;font-weight:700">{company} - {title}</div>'
    '<div style="color:#555;font-size:13px;margin:4px 0">{loc} | {sal} | posted {age}d ago'
    ' | <b>{score}% match</b> | {prio}</div>'
    '<div style="font-size:13px;margin:6px 0"><b>Skills:</b> {skills}</div>'
    '<a href="{url}" style="display:inline-block;margin-top:8px;background:#FF5A2A;color:#fff;'
    'padding:8px 16px;border-radius:999px;text-decoration:none;font-size:13px">Apply</a></div>'
)


def load_seen():
    if os.path.exists(SEEN_PATH):
        try:
            with open(SEEN_PATH) as f:
                return set(json.load(f))
        except (ValueError, OSError):
            return set()
    return set()


def save_seen(ids):
    with open(SEEN_PATH, "w") as f:
        json.dump(sorted(ids), f, indent=0)


def send_email(subject, html):
    user = os.environ["MAIL_USERNAME"]
    pw = os.environ["MAIL_APP_PASSWORD"]
    to = os.environ.get("MAIL_TO", user)
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())


def build_html(jobs):
    cards = "".join(
        CARD.format(
            company=j.company, title=j.title, loc=(j.location or "US"),
            sal=(j.salary or "salary n/a"), age=j.posted_days_ago, score=j.match_score,
            prio=j.priority, skills=(", ".join(j.req_skills) or "see listing"), url=j.apply_url,
        )
        for j in jobs
    )
    return (
        '<div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto">'
        "<h2>Jobwright - " + str(len(jobs)) + " new match(es)</h2>"
        '<p style="color:#666;font-size:13px">Fresh entry-level data roles, ranked to your '
        "resume. Apply links go straight to the company.</p>" + cards +
        '<p style="color:#999;font-size:12px">Sent automatically by your Jobwright agent. '
        "It never applies for you - that is your call.</p></div>"
    )


def main():
    found = search.discover()
    log.info("scanned %d listings", len(found))
    seen = load_seen()
    new = [j for j in found if j.job_id not in seen]
    ranked = rank.rank(new)
    for j in ranked:
        compose.enrich(j)
    log.info("%d new after dedupe, %d fresh and ranked", len(new), len(ranked))

    if ranked:
        send_email("Jobwright: " + str(len(ranked)) + " new job match(es)", build_html(ranked))
        log.info("digest emailed")
    elif not found:
        send_email(
            "Jobwright: scan came back empty (worth a look)",
            "<p>This run found 0 listings across all boards. The source markup may have "
            "changed or the network hiccuped. If it repeats, the scraper needs a tweak.</p>",
        )
        log.info("empty-scan alert emailed")
    else:
        log.info("no new matches this run - nothing to send")

    save_seen(seen | {j.job_id for j in found})


if __name__ == "__main__":
    main()
