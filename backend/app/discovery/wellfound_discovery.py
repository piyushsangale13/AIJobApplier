import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.core.config import get_settings
from app.core.logging import get_logger
from app.discovery.base import BaseDiscoverySource
from app.schemas.job import DiscoveredJob, JobDiscoveryRequest


logger = get_logger(__name__)


class WellfoundDiscovery(BaseDiscoverySource):
    source_name = "wellfound"

    async def discover(self, request: JobDiscoveryRequest) -> list[DiscoveredJob]:
        settings = get_settings()
        jobs: list[DiscoveredJob] = []
        queries = self.build_queries(request)

        for query in queries:
            for location in settings.wellfound_search_locations:
                url = (
                    "https://wellfound.com/jobs?"
                    f"query={self.encode_query(query)}&location={self.encode_query(location)}"
                )
                try:
                    response = await self.client.get(url)
                    response.raise_for_status()
                except Exception as exc:
                    logger.warning("discovery.wellfound.request_failed", url=url, error=str(exc))
                    continue

                soup = self.parse_html(response.text)
                for card in soup.select("div[data-test='StartupResult'], div[data-test='JobListItem']"):
                    title_node = card.select_one("a[href*='/jobs/']")
                    company_node = card.select_one("[data-test='companyName'], a[href*='/company/']")
                    if not title_node:
                        continue
                    title = title_node.get_text(" ", strip=True)
                    company = company_node.get_text(" ", strip=True) if company_node else "Wellfound Company"
                    apply_url = urljoin("https://wellfound.com", title_node.get("href", ""))
                    source_id = hashlib.sha256(f"wellfound|{company}|{title}|{apply_url}".encode()).hexdigest()
                    jobs.append(
                        DiscoveredJob(
                            source_id=source_id,
                            company=company,
                            title=title,
                            location=location,
                            salary_text=None,
                            apply_url=apply_url,
                            description=card.get_text(" ", strip=True),
                            posted_at=datetime.now(timezone.utc),
                            source="wellfound",
                            metadata={"search_url": url},
                        )
                    )
                    if len(jobs) >= request.limit_per_source:
                        break
        return jobs[: request.limit_per_source]
