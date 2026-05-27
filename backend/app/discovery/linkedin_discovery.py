import asyncio
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.core.logging import get_logger
from app.discovery.base import BaseDiscoverySource
from app.schemas.job import DiscoveredJob, JobDiscoveryRequest


logger = get_logger(__name__)

_DESCRIPTION_SELECTORS = [
    ".show-more-less-html__markup",
    ".description__text",
    "section.description div",
    "div.decorated-job-posting__details",
]


class LinkedInDiscovery(BaseDiscoverySource):
    source_name = "linkedin"

    async def discover(self, request: JobDiscoveryRequest) -> list[DiscoveredJob]:
        meta_list: list[dict] = []
        seen_companies: set[str] = set()
        queries = self.build_queries(request)

        for query in queries:
            if len(meta_list) >= request.limit_per_source:
                break

            search_url = (
                "https://www.linkedin.com/jobs/search/"
                f"?keywords={self.encode_query(query)}"
            )
            try:
                response = await self.client.get(search_url)
                response.raise_for_status()
            except Exception as exc:
                logger.warning("discovery.linkedin.request_failed", url=search_url, error=str(exc))
                continue

            soup = self.parse_html(response.text)
            for card in soup.select("div.base-card, li div.base-card"):
                if len(meta_list) >= request.limit_per_source:
                    break
                title_node = card.select_one(".base-search-card__title")
                company_node = card.select_one(".base-search-card__subtitle")
                location_node = card.select_one(".job-search-card__location")
                link_node = card.select_one("a.base-card__full-link")
                if not title_node or not company_node or not link_node:
                    continue
                company = company_node.get_text(strip=True)
                if company in seen_companies:
                    continue
                seen_companies.add(company)
                apply_url = urljoin("https://www.linkedin.com", link_node.get("href", "").strip())
                meta_list.append(
                    {
                        "source_id": hashlib.sha256(
                            f"linkedin|{company}|{title_node.get_text(strip=True)}|{apply_url}".encode()
                        ).hexdigest(),
                        "company": company,
                        "title": title_node.get_text(strip=True),
                        "location": location_node.get_text(strip=True) if location_node else None,
                        "apply_url": apply_url,
                        "search_url": search_url,
                    }
                )

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
                    metadata={"search_url": meta["search_url"]},
                )
            )

        return jobs

    async def _fetch_description(self, job_url: str) -> str:
        try:
            response = await self.client.get(job_url)
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
