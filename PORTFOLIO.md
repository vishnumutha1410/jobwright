# Jobwright — Autonomous Job-Search & Application-Prep Agent

*Personal project · Python · 2026*
[GitHub](https://github.com/<you>/jobwright) · Data Engineering / Automation

---

## The problem

Searching for entry-level data-engineering roles is repetitive, manual work: checking a
dozen job boards daily, re-reading near-identical listings, deduping what you've already
seen, and rewriting the same application note for each company. It's exactly the kind of
brittle, repeated process a data pipeline should own.

## The solution

**Jobwright** is an autonomous agent that runs on a schedule and turns the job hunt into a
pipeline. Each run it discovers fresh postings across public boards, resolves the *direct*
company application link, scores every role against my resume, writes a tailored application
note plus interview-prep notes, and saves a ready-to-review **Gmail draft** for each strong
match. It never sends anything — I stay in control of the final apply.

## How it works

```
Scheduler (every 3h)
      │
      ▼
Discover ──▶ Resolve direct apply URL ──▶ Dedupe (history store)
      │
      ▼
Rank (skills · location · recency · salary)  ──▶  Compose note + interview tips
      │                                                   │
      ▼                                                   ▼
Persist to Excel tracker (Jobs + History)      Create Gmail draft per match
```

- **Ingestion (ETL-style):** fetches and parses multiple job boards, normalizes each posting
  into a typed `Job` record, and extracts required skills from the listing text.
- **Scoring engine:** a weighted 0–100 model — 60% skills overlap, 15% location preference,
  15% recency, 10% salary signal — with High / Medium / Low prioritization.
- **Dedupe / history:** every posting gets a stable hash ID recorded in a history sheet, so
  the agent never re-notifies me about a job I've already seen.
- **Generation:** builds a customized application note (referencing my real projects) plus a
  skill-gap list and interview-prep sheet.
- **Delivery:** creates Gmail drafts through the Gmail API; humans stay in the loop by design.

## Tech stack

`Python` · `requests` · `BeautifulSoup` · `openpyxl` · `Gmail API (OAuth)` · `APScheduler` · `dotenv`

## Highlights / results

- End-to-end **agentic pipeline** with a scheduler, dedupe layer, and third-party API integration.
- **Freshness + active-only filtering** (posted ≤ 7 days) so results are always applyable.
- **Direct-apply URL resolution** — lands on the real Greenhouse/Ashby/Lever/Workday page, not an aggregator.
- Cut a daily ~1-hour manual search-and-draft routine down to a **hands-off review of pre-written drafts**.
- Clean, modular, testable design (7 focused modules); storage backend swappable to SQLite.

## Résumé bullet points (copy-paste)

- Built **Jobwright**, an autonomous Python agent that discovers, scores, and prepares
  applications for entry-level data-engineering roles, cutting a daily ~1-hour manual routine
  to a hands-off review of pre-written email drafts.
- Designed a weighted **0–100 matching engine** (skills overlap, location, recency, salary)
  with High/Medium/Low prioritization and a hash-based **dedupe/history store** to prevent
  duplicate notifications.
- Implemented **ETL-style ingestion** with `requests`/`BeautifulSoup`, resolving direct
  company/ATS apply URLs, and persisted results to a structured Excel tracker.
- Integrated the **Gmail API (OAuth)** to auto-generate tailored, review-ready application
  drafts, and scheduled recurring runs every 3 hours with `APScheduler`.
