from pathlib import Path

from playwright.async_api import BrowserContext, Page, async_playwright

from app.core.config import get_settings


class BrowserManager:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def launch(self, profile_name: str = "default") -> tuple[object, BrowserContext, Page]:
        playwright = await async_playwright().start()
        profile_dir = Path(self.settings.storage_path) / "browser-profiles" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1440, "height": 980},
        )
        page = context.pages[0] if context.pages else await context.new_page()
        return playwright, context, page
