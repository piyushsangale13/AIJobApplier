from pydantic import BaseModel


class DashboardStats(BaseModel):
    jobs_found_today: int
    applications_submitted: int
    pending_applications: int
    failed_applications: int
