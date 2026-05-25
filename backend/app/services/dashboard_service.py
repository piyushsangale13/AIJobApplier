from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.schemas.dashboard import DashboardStats


class DashboardService:
    def __init__(
        self, job_repository: JobRepository, application_repository: ApplicationRepository
    ) -> None:
        self.job_repository = job_repository
        self.application_repository = application_repository

    async def get_stats(self) -> DashboardStats:
        return DashboardStats(
            jobs_found_today=await self.job_repository.count_created_today(),
            applications_submitted=await self.application_repository.count_by_status("applied"),
            pending_applications=await self.application_repository.count_by_status("pending"),
            failed_applications=await self.application_repository.count_by_status("failed"),
        )
