from app.automation.base_handler import BaseATSHandler
from app.models.job import Job
from app.models.resume import Resume


class WorkdayHandler(BaseATSHandler):
    ats_type = "workday"

    async def open_application(self, job: Job) -> None:
        await self.page.goto(job.apply_url, wait_until="domcontentloaded")

    async def upload_resume(self, resume: Resume) -> None:
        await self.upload_from_common_inputs(resume.file_path)

    async def fill_forms(self, job: Job, resume: Resume) -> None:
        data = resume.parsed_data
        await self.type_if_visible(["input[name*='email']", "input[type='email']"], data.get("email") or "")
        await self.type_if_visible(["input[name*='legalName']", "input[name*='name']"], data.get("name") or "")

    async def submit_application(self) -> None:
        button = self.page.locator("button[data-automation-id='bottom-navigation-next-button'], button[type='submit']").first
        if await button.count():
            await button.click()
