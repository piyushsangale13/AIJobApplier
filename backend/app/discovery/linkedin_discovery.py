import asyncio
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.core.logging import get_logger
from app.discovery.base import BaseDiscoverySource
from app.schemas.job import DiscoveredJob, JobDiscoveryRequest


logger = get_logger(__name__)

_SEARCH_URL = "https://www.linkedin.com/jobs/search/"

# Realistic browser headers reduce bot-detection blocks.
_BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

_DESCRIPTION_SELECTORS = [
    ".show-more-less-html__markup",
    ".description__text",
    "section.description div",
    "div.decorated-job-posting__details",
]

# Maps common experience-level strings to LinkedIn's f_E filter codes.
_EXP_LEVEL_MAP = {
    "intern": "1", "internship": "1",
    "entry": "2", "junior": "2", "fresher": "2", "sde1": "2", "sde 1": "2",
    "associate": "3",
    "mid": "4", "senior": "4", "sde2": "4", "sde 2": "4", "lead": "4",
    "director": "5",
    "executive": "6", "vp": "6", "c-level": "6",
}


def _experience_codes(experience_levels: list[str]) -> list[str]:
    codes: list[str] = []
    for level in experience_levels:
        code = _EXP_LEVEL_MAP.get(level.lower().strip())
        if code and code not in codes:
            codes.append(code)
    return codes


class LinkedInDiscovery(BaseDiscoverySource):
    source_name = "linkedin"

    async def discover(self, request: JobDiscoveryRequest) -> list[DiscoveredJob]:
        keywords_list = request.keywords or ["software engineer"]
        locations = request.locations or ["India"]
        exp_codes = _experience_codes(request.experience_levels or [])

        meta_list: list[dict] = []
        seen_ids: set[str] = set()

        for keyword in keywords_list:
            for location in locations:
                if len(meta_list) >= request.limit_per_source:
                    break
                fetched = await self._search_one(
                    keyword=keyword,
                    location=location,
                    remote_only=request.remote_only,
                    exp_codes=exp_codes,
                    limit=request.limit_per_source - len(meta_list),
                )
                for item in fetched:
                    if item["source_id"] not in seen_ids:
                        seen_ids.add(item["source_id"])
                        meta_list.append(item)
                # Small pause between location queries to reduce rate-limiting.
                await asyncio.sleep(0.5)

        descriptions = await asyncio.gather(
            *(self._fetch_description(m["apply_url"]) for m in meta_list),
            return_exceptions=True,
        )

        jobs: list[DiscoveredJob] = []
        for meta, desc in zip(meta_list, descriptions):
            description = desc if isinstance(desc, str) and desc.strip() else meta["title"]
            jobs.append(
                DiscoveredJob(
                    source_id=meta["source_id"],
                    company=meta["company"],
                    title=meta["title"],
                    location=meta["location"],
                    salary_text=None,
                    apply_url=meta["apply_url"],
                    description=description,
                    posted_at=datetime.now(timezone.utc),
                    source="linkedin",
                    metadata={"search_location": meta["search_location"]},
                )
            )
        return jobs

    async def _search_one(
        self,
        keyword: str,
        location: str,
        remote_only: bool,
        exp_codes: list[str],
        limit: int,
    ) -> list[dict]:
        """Fetch one page of job cards for a single keyword + location pair."""
        params: dict[str, str | int] = {
            "keywords": keyword,
            "location": location,    # proper location filter — NOT embedded in keyword string
            "start": 0,
        }
        if remote_only:
            params["f_WT"] = "2"     # LinkedIn work-type: 2 = Remote
        if exp_codes:
            params["f_E"] = ",".join(exp_codes)

        try:
            response = await self.client.get(
                _SEARCH_URL,
                params=params,
                headers=_BROWSER_HEADERS,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.warning(
                "discovery.linkedin.search_failed",
                keyword=keyword,
                location=location,
                error=str(exc),
            )
            return []

        soup = self.parse_html(response.text)
        cards = soup.select("div.base-card")
        if not cards:
            logger.warning(
                "discovery.linkedin.no_cards",
                keyword=keyword,
                location=location,
                status_code=response.status_code,
                html_snippet=response.text[:500],
            )
            return []

        results: list[dict] = []

        for card in cards:
            if len(results) >= limit:
                break
            title_node = card.select_one(".base-search-card__title")
            company_node = card.select_one(".base-search-card__subtitle")
            location_node = card.select_one(".job-search-card__location")
            link_node = card.select_one("a.base-card__full-link")

            if not title_node or not company_node or not link_node:
                continue

            apply_url = urljoin("https://www.linkedin.com", link_node.get("href", "").strip())

            # Prefer the stable job-posting URN; fall back to hashing.
            urn = card.get("data-entity-urn", "")
            source_id = urn if urn else hashlib.sha256(
                f"linkedin|{company_node.get_text(strip=True)}|{title_node.get_text(strip=True)}|{apply_url}".encode()
            ).hexdigest()

            results.append(
                {
                    "source_id": source_id,
                    "company": company_node.get_text(strip=True),
                    "title": title_node.get_text(strip=True),
                    "location": location_node.get_text(strip=True) if location_node else location,
                    "apply_url": apply_url,
                    "search_location": location,
                }
            )

        return results

    async def _fetch_description(self, job_url: str) -> str:
        try:
            response = await self.client.get(job_url, headers=_BROWSER_HEADERS)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            for selector in _DESCRIPTION_SELECTORS:
                node = soup.select_one(selector)
                if node:
                    text = node.get_text(" ", strip=True)
                    if len(text) > 100:
                        return text
        except Exception as exc:
            logger.warning("discovery.linkedin.description_fetch_failed", url=job_url, error=str(exc))
        return ""
