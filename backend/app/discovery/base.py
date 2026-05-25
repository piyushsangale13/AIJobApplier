from abc import ABC, abstractmethod
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from httpx import AsyncClient

from app.schemas.job import DiscoveredJob, JobDiscoveryRequest


class BaseDiscoverySource(ABC):
    source_name: str

    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    @abstractmethod
    async def discover(self, request: JobDiscoveryRequest) -> list[DiscoveredJob]:
        raise NotImplementedError

    def build_queries(self, request: JobDiscoveryRequest) -> list[str]:
        base_keywords = request.keywords or ["software engineer"]
        locations = request.locations or ["India"]
        experience_levels = request.experience_levels or [""]
        queries: list[str] = []
        for keyword in base_keywords:
            for location in locations:
                for experience_level in experience_levels:
                    parts = [keyword, experience_level, location]
                    query = " ".join(part.strip() for part in parts if part and part.strip())
                    if query:
                        queries.append(query)
        return list(dict.fromkeys(queries))

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def encode_query(self, query: str) -> str:
        return quote_plus(query)
