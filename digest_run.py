"""Jobwright cloud runner - one Gmail DRAFT per new job, with YOUR resume attached.

Each new matching role becomes a Gmail draft containing: a personalized cover note,
pre-written answers to standard screening questions, interview tips, the direct apply
link, and your real resume (resume.pdf) attached. You review, upload, and submit.
Never sends, never applies.  Env: MAIL_USERNAME, MAIL_APP_PASSWORD, MAIL_TO (optional).
"""
import os
import json
import time
import imaplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate

from jobwright import search, rank, compose
import applicant

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("jobwright")
SEEN_PATH = "seen.json"
RESUME_PATH = "resume.pdf"
RESUME_FILENAME = "Vishnu_Vardhan_Mutha_Resume.pdf"
DRAFTS_MAILBOX = '"[Gmail]/Drafts"'


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


def _answers_block():
    lines = ["--- APPLICATION ANSWERS (copy into the form) ---"]
    for k, v in applicant.ANSWERS.items():
        lines.append(k + ": " + v)
    return "\n".join(lines)


def create_draft(subject, body, attach=True):
    user = os.environ["MAIL_USERNAME"]
    pw = os.environ["MAIL_APP_PASSWORD"]
    to = os.environ.get("MAIL_TO", user)
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(body, "plain"))
    if attach and os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=RESUME_FILENAME)
        msg.attach(part)
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, pw)
    imap.append(DRAFTS_MAILBOX, "\\Draft", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    imap.logout()


def main():
    found = search.discover()
    log.info("scanned %d listings", len(found))
    seen = load_seen()
    new = [j for j in found if j.job_id not in seen]
    ranked = rank.rank(new)
    for j in ranked:
        compose.enrich(j)
    log.info("%d new after dedupe, %d fresh and ranked", len(new), len(ranked))

    made = 0
    for j in ranked:
        body = compose.email_body(j) + "\n\n" + _answers_block() + \
            "\n\n[Your resume is attached - upload it when applying.]"
        subject = "Application - %s at %s (%d%% match)" % (j.title, j.company, j.match_score)
        create_draft(subject, body, attach=True)
        made += 1

    if made:
        log.info("created %d application-package drafts", made)
    elif not found:
        create_draft("Jobwright: scan came back empty (worth a look)",
                     "This run found 0 listings across all boards. The source markup may have "
                     "changed or the network hiccuped. If it repeats, the scraper needs a tweak.",
                     attach=False)
        log.info("empty-scan alert drafted")
    else:
        log.info("no new matches this run - nothing drafted")

    save_seen(seen | {j.job_id for j in found})


if __name__ == "__main__":
    main()
