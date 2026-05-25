import asyncio
from abc import ABC, abstractmethod
from pathlib import Path

from playwright.async_api import BrowserContext, Page
from tenacity import retry, stop_after_attempt, wait_random_exponential

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume


logger = get_logger(__name__)


class BaseATSHandler(ABC):
    ats_type: str

    def __init__(self, page: Page) -> None:
        self.page = page
        self.settings = get_settings()

    @retry(wait=wait_random_exponential(multiplier=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def apply(self, job: Job, resume: Resume, application: Application) -> None:
        try:
            await self.open_application(job)
            await self.upload_resume(resume)
            await self.fill_forms(job, resume)
            await self.submit_application()
        except Exception as exc:
            screenshot = await self.capture_failure_screenshot(application.id)
            logger.error(
                "automation.apply_failed",
                ats_type=self.ats_type,
                job_id=job.id,
                application_id=application.id,
                error=str(exc),
                screenshot=screenshot,
            )
            raise

    @abstractmethod
    async def open_application(self, job: Job) -> None:
        raise NotImplementedError

    @abstractmethod
    async def upload_resume(self, resume: Resume) -> None:
        raise NotImplementedError

    @abstractmethod
    async def fill_forms(self, job: Job, resume: Resume) -> None:
        raise NotImplementedError

    @abstractmethod
    async def submit_application(self) -> None:
        raise NotImplementedError

    async def human_delay(self, minimum: float = 0.4, maximum: float = 1.2) -> None:
        await asyncio.sleep(minimum if minimum == maximum else (minimum + maximum) / 2)

    async def type_if_visible(self, selectors: list[str], value: str) -> bool:
        for selector in selectors:
            locator = self.page.locator(selector).first
            if await locator.count():
                await locator.fill("")
                await locator.type(value, delay=55)
                return True
        return False

    async def capture_failure_screenshot(self, application_id: str) -> str:
        target = Path(self.settings.screenshot_path) / f"{application_id}-{self.ats_type}.png"
        await self.page.screenshot(path=str(target), full_page=True)
        return str(target)

    async def upload_from_common_inputs(self, resume_path: str) -> bool:
        selectors = [
            "input[type='file']",
            "input[name*='resume']",
            "input[id*='resume']",
        ]
        for selector in selectors:
            locator = self.page.locator(selector).first
            if await locator.count():
                await locator.set_input_files(resume_path)
                return True
        return False
