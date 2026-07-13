"""Central configuration for Jobwright: candidate profile, targets, sources, weights."""
import os

CANDIDATE = {
    "name": "Vishnu Vardhan Mutha",
    "email": "vishnumutha1410@gmail.com",
    "home_state": "TX",
    "core_skills": [
        "sql", "python", "pandas", "numpy", "snowflake", "dbt", "airflow",
        "pyspark", "spark", "docker", "aws", "azure", "gcp", "postgresql", "postgres",
        "etl", "elt", "data warehousing", "star schema", "medallion", "data quality",
        "power bi", "tableau", "looker", "bigquery", "redshift", "databricks",
    ],
    "projects": {
        "AgentOps": "AI-agent analytics platform (S3, Snowflake, dbt, FastAPI, Airflow, Docker).",
        "Wildfire/Air-Quality Pipeline": "Hourly REST-API ELT into Snowflake, dbt, 8 tests, Airflow.",
        "Netflix EDA": "8,800+ titles with Pandas.",
        "IPL EDA": "180,000+ records with Pandas.",
    },
}

# Broad target titles across data engineering + analytics + BI (entry/junior).
TARGET_TITLES = [
    "data engineer", "analytics engineer", "data analyst", "bi engineer",
    "business intelligence", "bi developer", "bi analyst", "data platform engineer",
    "etl developer", "data warehouse", "reporting analyst", "data quality",
    "junior data", "associate data", "data operations", "data pipeline",
]
ENTRY_SIGNALS = ["entry", "junior", "associate", "new grad", "fresher", "0-2", "0 to 2", "i "]

# US-wide; these get a ranking boost (preference, not a filter).
PREFERRED_LOCATIONS = ["remote", "texas", "austin", "dallas", "houston", "san antonio", "tx"]

# Openly-accessible Built In boards across data engineering, analytics, BI, and key metros.
SOURCE_BOARDS = [
    # data engineering (national + remote)
    "https://builtin.com/jobs/data-analytics/data-engineering/entry-level",
    "https://builtin.com/jobs/remote/data-analytics/data-engineering/entry-level",
    # whole data-analytics category (DA + BI + AE), national + remote
    "https://builtin.com/jobs/data-analytics/entry-level",
    "https://builtin.com/jobs/remote/data-analytics/entry-level",
    # keyword searches for the analyst / AE / BI side
    "https://builtin.com/jobs/remote/data-analytics/search/analytics-engineer",
    "https://builtin.com/jobs/data-analytics/search/data-analyst",
    "https://builtin.com/jobs/remote/data-analytics/search/data-analyst",
    "https://builtin.com/jobs/data-analytics/search/business-intelligence",
    # Texas metros (preference)
    "https://www.builtinaustin.com/jobs/data-analytics/entry-level",
    "https://builtin.com/jobs/dallas-fort-worth/data-analytics/entry-level",
    "https://builtin.com/jobs/houston/data-analytics/entry-level",
]

WEIGHTS = {"skills": 0.55, "location": 0.15, "recency": 0.15, "salary": 0.15}
PRIORITY_THRESHOLDS = {"High": 75, "Medium": 55}
MAX_POSTING_AGE_DAYS = int(os.getenv("MAX_POSTING_AGE_DAYS", "7"))
