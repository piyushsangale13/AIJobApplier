import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.core.config import get_settings
from app.core.logging import get_logger
from app.discovery.base import BaseDiscoverySource
from app.schemas.job import DiscoveredJob, JobDiscoveryRequest


logger = get_logger(__name__)


class LinkedInDiscovery(BaseDiscoverySource):
    source_name = "linkedin"

    async def discover(self, request: JobDiscoveryRequest) -> list[DiscoveredJob]:
        settings = get_settings()
        jobs: list[DiscoveredJob] = []
        queries = self.build_queries(request)
        for query in queries:
            for location in settings.linkedin_search_locations:
                search_url = (
                    "https://www.linkedin.com/jobs/search/"
                    f"?keywords={self.encode_query(query)}&location={self.encode_query(location)}"
                )
                try:
                    response = await self.client.get(search_url)
                    response.raise_for_status()
                except Exception as exc:
                    logger.warning("discovery.linkedin.request_failed", url=search_url, error=str(exc))
                    continue

                soup = self.parse_html(response.text)
                cards = soup.select("div.base-card, li div.base-card")
                for card in cards[: request.limit_per_source]:
                    title_node = card.select_one(".base-search-card__title")
                    company_node = card.select_one(".base-search-card__subtitle")
                    location_node = card.select_one(".job-search-card__location")
                    link_node = card.select_one("a.base-card__full-link")
                    if not title_node or not company_node or not link_node:
                        continue
                    apply_url = urljoin("https://www.linkedin.com", link_node.get("href", "").strip())
                    source_id = hashlib.sha256(
                        f"linkedin|{company_node.get_text(strip=True)}|{title_node.get_text(strip=True)}|{apply_url}".encode()
                    ).hexdigest()
                    jobs.append(
                        DiscoveredJob(
                            source_id=source_id,
                            company=company_node.get_text(strip=True),
                            title=title_node.get_text(strip=True),
                            location=location_node.get_text(strip=True) if location_node else location,
                            salary_text=None,
                            apply_url=apply_url,
                            description=card.get_text(" ", strip=True),
                            posted_at=datetime.now(timezone.utc),
                            source="linkedin",
                            metadata={"search_url": search_url},
                        )
                    )
        return jobs
