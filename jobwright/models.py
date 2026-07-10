"""Shared data model for a job posting."""
from dataclasses import dataclass, field
from datetime import date
import hashlib


@dataclass
class Job:
    company: str
    title: str
    location: str = ""
    salary: str = ""
    employment_type: str = ""
    experience: str = ""
    req_skills: list = field(default_factory=list)
    posted_days_ago: int = 999
    listing_url: str = ""       # Built In (source) listing
    apply_url: str = ""         # direct company/ATS application URL
    # Computed downstream:
    match_score: int = 0
    priority: str = "Low"
    why_match: str = ""
    skill_gaps: str = ""
    note: str = ""
    interview_tips: str = ""
    date_found: str = field(default_factory=lambda: date.today().isoformat())

    @property
    def job_id(self) -> str:
        """Stable fingerprint for dedupe (company + title)."""
        return hashlib.md5(f"{self.company}|{self.title}".encode()).hexdigest()[:10]
