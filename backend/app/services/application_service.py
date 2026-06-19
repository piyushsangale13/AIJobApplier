from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.automation.browser_manager import BrowserManager
from app.automation.router import get_handler_class
from app.core.logging import get_logger
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.application import ApplicationRead


logger = get_logger(__name__)


class ApplicationService:
    def __init__(
        self,
        application_repository: ApplicationRepository,
        job_repository: JobRepository,
        resume_repository: ResumeRepository,
    ) -> None:
        self.application_repository = application_repository
        self.job_repository = job_repository
        self.resume_repository = resume_repository
        self.browser_manager = BrowserManager()

    async def list_applications(self) -> list[ApplicationRead]:
        items = await self.application_repository.list_all()
        return [ApplicationRead.model_validate(item) for item in items]

    async def process_pending_queue(self, limit: int = 5) -> list[ApplicationRead]:
        applications = await self.application_repository.list_pending(limit=limit)
        processed: list[ApplicationRead] = []
        for application in applications:
            job = await self.job_repository.get_by_id(application.job_id) if application.job_id else None
            resume = await self.resume_repository.get_by_id(application.resume_id) if application.resume_id else None
            if not job or not resume:
                continue

            handler_class = get_handler_class(job.ats_type)
            if not handler_class:
                application.status = "requires_manual_action"
                application.notes = f"No automation handler registered for ATS type {job.ats_type}."
                await self.application_repository.create_or_update_for_job(
                    {
                        "job_id": application.job_id,
                        "resume_id": application.resume_id,
                        "company": application.company,
                        "role": application.role,
                        "status": application.status,
                        "notes": application.notes,
                        "screenshots": application.screenshots,
                    }
                )
                processed.append(ApplicationRead.model_validate(application))
                continue

            application.status = "applying"
            await self.application_repository.create_or_update_for_job(
                {
                    "job_id": application.job_id,
                    "resume_id": application.resume_id,
                    "company": application.company,
                    "role": application.role,
                    "status": application.status,
                    "notes": application.notes,
                    "screenshots": application.screenshots,
                }
            )

            playwright, context, page = await self.browser_manager.launch()
            try:
                handler = handler_class(page)
                await handler.apply(job, resume, application)
                application.status = "applied"
                application.applied_at = datetime.now(timezone.utc)
            except Exception as exc:
                logger.error("automation.queue_item_failed", application_id=application.id, error=str(exc))
                application.status = "failed"
                application.notes = str(exc)
            finally:
                await context.close()
                await playwright.stop()

            saved = await self.application_repository.create_or_update_for_job(
                {
                    "job_id": application.job_id,
                    "resume_id": application.resume_id,
                    "company": application.company,
                    "role": application.role,
                    "status": application.status,
                    "applied_at": application.applied_at,
                    "resume_version": application.resume_version,
                    "notes": application.notes,
                    "screenshots": application.screenshots,
                }
            )
            processed.append(ApplicationRead.model_validate(saved))

        return processed
