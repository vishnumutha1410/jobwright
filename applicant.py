"""Vishnu's structured resume + standard application answers (single source of truth)."""

CONTACT = {
    "name": "Vishnu Vardhan Mutha",
    "title": "Data Engineer",
    "location": "Leander, TX, USA",
    "email": "vishnumutha1410@gmail.com",
    "phone": "+1 737-230-2551",
    "linkedin": "linkedin.com/in/vishnu-vardhan-mutha-5187942b9",
    "github": "github.com/vishnumutha1410",
}

SUMMARY = (
    "Data Engineer skilled in building end-to-end ELT pipelines, cloud data warehouses, and "
    "automated transformation layers. Hands-on with {focus}. M.S. in Data Analytics (Webster "
    "University). Seeking entry-level Data Engineer / Analytics Engineer roles in the USA."
)

# Master skill list (order gets tailored per job).
SKILLS = [
    "SQL", "Python", "Pandas", "NumPy", "Snowflake", "dbt", "Apache Airflow", "PySpark",
    "Docker", "AWS", "PostgreSQL", "ETL/ELT", "Data Warehousing", "Star Schema Modeling",
    "Data Quality Testing", "Power BI", "Tableau", "Git", "REST APIs",
]

PROJECTS = [
    {"name": "AgentOps - AI Agent Analytics Platform", "year": "2026",
     "stack": "Python, AWS S3, Snowflake, dbt, FastAPI, Airflow, Docker",
     "bullets": [
         "Built an end-to-end observability platform processing 100,000 synthetic requests through a Bronze/Silver/Gold pipeline: AWS S3 data lake, Pandas validation, and a Snowflake warehouse.",
         "Modeled a star schema in dbt (4 staging views, 4 fact/dimension tables) with 16 automated data-quality tests, exposed via a FastAPI service with 8 REST endpoints.",
         "Orchestrated the full generate-to-warehouse pipeline with an hourly Airflow DAG; containerized with Docker.",
     ]},
    {"name": "Wildfire Risk & Air Quality Pipeline", "year": "2026",
     "stack": "Python, Snowflake, dbt, Airflow, Docker, REST API, SQL",
     "bullets": [
         "Engineered a production-style ELT pipeline ingesting live weather/air-quality data for 6 US regions hourly into a Snowflake warehouse.",
         "Built 3 dbt models computing a 0-100 fire-risk score and WHO/EPA PM2.5 health bands, with 8 automated data-quality tests (all passing).",
         "Orchestrated ingest -> dbt run -> dbt test with an Airflow DAG; containerized with Docker for reproducible deployment.",
     ]},
    {"name": "Netflix Content Analysis - EDA", "year": "2025",
     "stack": "Python, Pandas, Matplotlib, Seaborn, Jupyter",
     "bullets": [
         "Analyzed 8,800+ Netflix titles to surface content trends, genre distribution, and catalog growth (2008-2021).",
         "Produced 6 publication-ready visualizations; published a clean, documented pipeline on GitHub.",
     ]},
    {"name": "IPL Data Analysis - EDA", "year": "2026",
     "stack": "Python, Pandas, Matplotlib, Seaborn",
     "bullets": [
         "Joined 2 CSV datasets (180,000+ ball-by-ball records across 13 seasons) with Pandas to surface player, team, and venue insights.",
         "Produced 6 visualizations; packaged as a standalone script, notebook, and documented README.",
     ]},
]

EDUCATION = [
    "M.S., Data Analytics - Webster University, USA (Aug 2024 - Jun 2026)",
    "B.Tech, Computer Science - Samskruthi Engineering College, India (2023)",
]

CERTIFICATIONS = [
    "Google Data Analytics - Google/Coursera",
    "Introduction to Data Engineering - IBM/Coursera",
    "Cloud Onboarding for SAP Cloud ERP - SAP",
]

# Standard screening/knockout answers (from your intake).
ANSWERS = {
    "Full name": CONTACT["name"],
    "Email": CONTACT["email"],
    "Phone": CONTACT["phone"],
    "Location": CONTACT["location"],
    "LinkedIn": CONTACT["linkedin"],
    "GitHub": CONTACT["github"],
    "Work authorization": "Authorized to work in the US on F-1 OPT/CPT (work-authorized now).",
    "Require sponsorship?": "Not now - authorized on F-1 OPT. Will require H-1B sponsorship in the future.",
    "Willing to relocate?": "Yes. Prefer remote; also open to on-site/hybrid in Texas (Austin/Dallas/Houston) and will relocate within the US for the right role.",
    "Salary expectation": "$70,000 - $90,000 (flexible/negotiable).",
    "Notice period / availability": "Immediately available.",
    "Years of experience": "Entry-level / new graduate (0-2 years via projects, internships, and coursework).",
    "Highest education": EDUCATION[0],
}


def tailor_skills(job_skills):
    """Free keyword tailoring: put skills the JD mentions first, keep the rest."""
    jl = [s.lower() for s in (job_skills or [])]
    def hit(sk):
        s = sk.lower()
        return any(j in s or s in j for j in jl)
    matched = [s for s in SKILLS if hit(s)]
    rest = [s for s in SKILLS if s not in matched]
    return matched + rest, matched


def tailored_summary(matched):
    focus = ", ".join(matched[:5]) if matched else "SQL, Python, Snowflake, dbt, Airflow"
    return SUMMARY.format(focus=focus)
