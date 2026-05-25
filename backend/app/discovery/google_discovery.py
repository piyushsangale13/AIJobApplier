import hashlib
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from app.core.config import get_settings
from app.core.logging import get_logger
from app.discovery.base import BaseDiscoverySource
from app.schemas.job import DiscoveredJob, JobDiscoveryRequest


logger = get_logger(__name__)


class GoogleDiscovery(BaseDiscoverySource):
    source_name = "google"

    async def discover(self, request: JobDiscoveryRequest) -> list[DiscoveredJob]:
        settings = get_settings()
        jobs: list[DiscoveredJob] = []
        queries = self.build_queries(request)

        for query in queries:
            for domain in settings.google_search_domains:
                search_query = f'site:{domain} "{query}"'
                url = f"https://www.google.com/search?q={self.encode_query(search_query)}&num={request.limit_per_source}"
                try:
                    response = await self.client.get(url)
                    response.raise_for_status()
                except Exception as exc:
                    logger.warning("discovery.google.request_failed", url=url, error=str(exc))
                    continue

                soup = self.parse_html(response.text)
                for anchor in soup.select("a[href^='/url?q=']"):
                    href = anchor.get("href", "")
                    parsed = parse_qs(urlparse(href).query)
                    target = parsed.get("q", [None])[0]
                    if not target:
                        continue
                    title = anchor.get_text(" ", strip=True)
                    if not title:
                        continue
                    company = self._extract_company_from_url(target)
                    source_id = hashlib.sha256(f"google|{company}|{title}|{target}".encode()).hexdigest()
                    jobs.append(
                        DiscoveredJob(
                            source_id=source_id,
                            company=company,
                            title=title,
                            location=(request.locations[0] if request.locations else "India"),
                            salary_text=None,
                            apply_url=target,
                            description=f"Google-discovered listing for {title} at {company}",
                            posted_at=datetime.now(timezone.utc),
                            source="google",
                            metadata={"query": search_query, "domain": domain},
                        )
                    )
                    if len(jobs) >= request.limit_per_source:
                        break
        return jobs[: request.limit_per_source * max(1, len(settings.google_search_domains))]

    def _extract_company_from_url(self, url: str) -> str:
        host = urlparse(url).netloc.replace("www.", "")
        if host.startswith("jobs.lever.co"):
            parts = urlparse(url).path.strip("/").split("/")
            return parts[0].replace("-", " ").title() if parts else "Lever Company"
        if "greenhouse.io" in host:
            parts = urlparse(url).path.strip("/").split("/")
            if parts:
                return parts[0].replace("-", " ").title()
        return host.split(".")[0].replace("-", " ").title()
