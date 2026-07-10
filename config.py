"""Central configuration for Jobwright: candidate profile, targets, and scoring weights."""
import os
from dotenv import load_dotenv

load_dotenv()

# ---- Candidate profile (edit to your own) ----
CANDIDATE = {
    "name": "Vishnu Vardhan Mutha",
    "email": "vishnumutha1410@gmail.com",
    "home_state": "TX",
    # Skills weighted fully in match scoring.
    "core_skills": [
        "sql", "python", "pandas", "numpy", "snowflake", "dbt", "airflow",
        "pyspark", "docker", "aws", "postgresql", "etl", "elt",
        "data warehousing", "star schema", "medallion", "data quality",
        "power bi", "tableau",
    ],
    # Projects referenced in generated application notes.
    "projects": {
        "AgentOps": "AI-agent observability platform (S3 data lake, Snowflake, dbt star schema "
                    "with 16 tests, FastAPI, Airflow, Docker).",
        "Wildfire/Air-Quality Pipeline": "Hourly REST-API ingest into Snowflake, dbt models, "
                                         "8 automated data-quality tests, Airflow, Docker.",
        "Netflix EDA": "Analyzed 8,800+ titles with Python/Pandas.",
        "IPL EDA": "Joined 180,000+ ball-by-ball records with Pandas.",
    },
}

# ---- Targets ----
TARGET_TITLES = [
    "data engineer", "analytics engineer", "data analyst", "bi engineer",
    "data platform engineer", "etl developer", "junior data engineer",
]
# Entry-level signals accepted in a listing's experience label.
ENTRY_SIGNALS = ["entry", "junior", "associate", "new grad", "fresher", "0-2", "0 to 2"]

# Nationwide search; these locations get a ranking boost (preference, not a filter).
PREFERRED_LOCATIONS = ["remote", "texas", "austin", "dallas", "houston", "san antonio", "tx"]

# ---- Built In source boards (open, structured, no login) ----
SOURCE_BOARDS = [
    "https://builtin.com/jobs/data-analytics/data-engineering/entry-level",
    "https://builtin.com/jobs/remote/data-analytics/data-engineering/entry-level",
    "https://builtin.com/jobs/remote/data-analytics/search/analytics-engineer",
    "https://www.builtinaustin.com/jobs/data-analytics/data-engineering/entry-level",
    "https://builtin.com/jobs/dallas-fort-worth/data-analytics/data-engineering/entry-level",
    "https://builtin.com/jobs/houston/data-analytics/data-engineering/entry-level",
]

# ---- Scoring weights (sum ~1.0) ----
WEIGHTS = {
    "skills": 0.60,     # overlap of required skills with core_skills
    "location": 0.15,   # preferred-location boost
    "recency": 0.15,    # newer postings score higher
    "salary": 0.10,     # listed salary is a small positive signal
}

MAX_POSTING_AGE_DAYS = int(os.getenv("MAX_POSTING_AGE_DAYS", "7"))
TRACKER_PATH = os.getenv("TRACKER_PATH", "Job_Search_Tracker.xlsx")
DRAFT_TO_EMAIL = os.getenv("DRAFT_TO_EMAIL", CANDIDATE["email"])
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")

PRIORITY_THRESHOLDS = {"High": 80, "Medium": 65}  # else Low
