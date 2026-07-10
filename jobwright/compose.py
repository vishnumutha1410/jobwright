"""Generate a personalized application note, interview tips, and email body."""
from config import CANDIDATE
from datetime import date


def _best_project() -> str:
    # Simple heuristic: AgentOps is the flagship; mention it plus one pipeline.
    return ("In my AgentOps project I built an end-to-end pipeline (AWS S3 data lake, "
            "Snowflake, dbt star schema with automated data-quality tests, Airflow, Docker), "
            "and in a second pipeline I ingest live REST-API data hourly into Snowflake with "
            "dbt models validated by automated tests.")


def application_note(job) -> str:
    return (
        f"Hi {job.company} team,\n\n"
        f"I'm applying for the {job.title} role and it lines up closely with what I build. "
        f"{_best_project()} I write reusable SQL and Python daily and care about pipeline "
        f"reliability and clean data models. I'd welcome the chance to contribute and grow "
        f"with your team. Thank you for your consideration.\n\n"
        f"Best,\n{CANDIDATE['name']}\n{CANDIDATE['email']}"
    )


def interview_tips(job) -> str:
    skills = ", ".join(job.req_skills[:4]) or "SQL and Python fundamentals"
    return (
        f"Review the core stack for this role ({skills}). Be ready to whiteboard an "
        f"ETL/ELT pipeline and explain your data-quality testing strategy. Prepare one "
        f"concrete story about catching and fixing a data problem."
    )


def email_body(job) -> str:
    return (
        "--- ROLE SNAPSHOT ---\n"
        f"Job Title: {job.title}\nCompany: {job.company}\nLocation: {job.location}\n"
        f"Posted: {job.posted_days_ago} day(s) ago  |  Status: ACTIVE as of {date.today().isoformat()}\n"
        f"Salary: {job.salary or 'Not listed'}\nResume Match Score: {job.match_score}%\n"
        f"Required Skills: {', '.join(job.req_skills) or 'See listing'}\n"
        f"APPLY HERE (direct company/ATS page): {job.apply_url}\n"
        f"Source listing: {job.listing_url}\n\n"
        f"--- PERSONALIZED MESSAGE ---\n{job.note}\n\n"
        f"--- SKILLS TO BRUSH UP ---\n{job.skill_gaps}\n\n"
        f"--- INTERVIEW PREP ---\n{job.interview_tips}\n"
    )


def enrich(job):
    job.note = application_note(job)
    job.interview_tips = interview_tips(job)
    return job
