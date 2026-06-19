from app.automation.base_handler import BaseATSHandler
from app.models.job import Job
from app.models.resume import Resume


class LinkedInEasyApplyHandler(BaseATSHandler):
    ats_type = "linkedin_easy_apply"

    async def open_application(self, job: Job) -> None:
        await self.page.goto(job.apply_url, wait_until="domcontentloaded")
        button = self.page.locator("button:has-text('Easy Apply'), button.jobs-apply-button").first
        if await button.count():
            await button.click()

    async def upload_resume(self, resume: Resume) -> None:
        await self.upload_from_common_inputs(resume.file_path)

    async def fill_forms(self, job: Job, resume: Resume) -> None:
        data = resume.parsed_data
        await self.type_if_visible(["input[type='email']", "input[name='emailAddress']"], data.get("email") or "")

    async def submit_application(self) -> None:
        button = self.page.locator("button[aria-label='Submit application'], button:has-text('Submit application')").first
        if await button.count():
            await button.click()
