import asyncio
from contextlib import suppress

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.search_preference_repository import SearchPreferenceRepository
from app.services.job_pipeline import JobPipelineService


logger = get_logger(__name__)


class JobDiscoveryScheduler:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if not self.settings.discovery_scheduler_enabled:
            logger.info("scheduler.disabled")
            return
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        if not self._task:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task

    async def _run_loop(self) -> None:
        interval_seconds = self.settings.discovery_interval_minutes * 60
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    pipeline = JobPipelineService(
                        job_repository=JobRepository(session),
                        resume_repository=ResumeRepository(session),
                        search_preference_repository=SearchPreferenceRepository(session),
                    )
                    await pipeline.discover_from_preferences()
                    logger.info("scheduler.discovery_cycle_completed")
            except Exception as exc:
                logger.error("scheduler.discovery_cycle_failed", error=str(exc))
            await asyncio.sleep(interval_seconds)
