import asyncio
from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.discovery import GoogleDiscovery, LinkedInDiscovery, WellfoundDiscovery
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.search_preference_repository import SearchPreferenceRepository
from app.schemas.job import DiscoveredJob, JobDiscoveryRequest, JobDiscoveryResponse, JobRead, JobScoreResponse
from app.services.ai_service import AIService
from app.utils.ats_detector import detect_ats_type


logger = get_logger(__name__)


class JobPipelineService:
    def __init__(
        self,
        job_repository: JobRepository,
        resume_repository: ResumeRepository,
        search_preference_repository: SearchPreferenceRepository,
        application_repository: ApplicationRepository,
        ai_service: AIService | None = None,
    ) -> None:
        self.job_repository = job_repository
        self.resume_repository = resume_repository
        self.search_preference_repository = search_preference_repository
        self.application_repository = application_repository
        self.ai_service = ai_service or AIService()
        self.settings = get_settings()

    async def discover_from_request(self, request: JobDiscoveryRequest) -> JobDiscoveryResponse:
        source_names = request.sources or ["linkedin", "google", "wellfound"]
        async with httpx.AsyncClient(
            timeout=self.settings.request_timeout_seconds,
            headers={"User-Agent": "Mozilla/5.0 AIJobApplier/0.2"},
            follow_redirects=True,
        ) as client:
            discovery_sources = self._build_sources(client, source_names)
            raw_results = await asyncio.gather(
                *(source.discover(request) for source in discovery_sources),
                return_exceptions=True,
            )

        source_counts: dict[str, int] = {}
        persisted_jobs: list[JobRead] = []
        seen_urls: set[str] = set()

        for source_name, result in zip(source_names, raw_results, strict=False):
            if isinstance(result, Exception):
                logger.warning("pipeline.discovery_source_failed", source=source_name, error=str(result))
                source_counts[source_name] = 0
                continue

            source_counts[source_name] = len(result)
            for discovered in result:
                if str(discovered.apply_url) in seen_urls:
                    continue
                seen_urls.add(str(discovered.apply_url))
                saved = await self._store_job(discovered)
                persisted_jobs.append(saved)

        return JobDiscoveryResponse(jobs=persisted_jobs, source_counts=source_counts, used_resume_id=None)

    async def discover_from_preferences(self) -> list[JobDiscoveryResponse]:
        preferences = await self.search_preference_repository.list_all(enabled_only=True)
        responses: list[JobDiscoveryResponse] = []
        for preference in preferences:
            request = JobDiscoveryRequest(
                keywords=preference.keywords,
                locations=preference.locations,
                experience_levels=[],
                sources=["linkedin", "google", "wellfound"],
                limit_per_source=self.settings.max_jobs_per_query,
                remote_only=False,
            )
            try:
                responses.append(await self.discover_from_request(request))
            except Exception as exc:
                logger.warning("pipeline.preference_discovery_failed", preference_id=preference.id, error=str(exc))
        return responses

    async def rescore_job(self, job_id: str, resume_id: str | None = None) -> JobScoreResponse:
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found.")
        resume = await self.resume_repository.get_by_id(resume_id) if resume_id else await self.resume_repository.get_latest()
        if not resume:
            raise ValueError("Resume not found. Upload a resume first.")
        score = await self.ai_service.score_job(resume.parsed_data, job.description)
        saved = await self.job_repository.upsert_job(
            {
                "source_id": job.source_id,
                "company": job.company,
                "title": job.title,
                "location": job.location,
                "salary_text": job.salary_text,
                "apply_url": job.apply_url,
                "ats_type": job.ats_type,
                "source": job.source,
                "description": job.description,
                "posted_at": job.posted_at,
                "discovered_at": job.discovered_at,
                "relevance_score": float(score.relevance_score),
                "ai_analysis": {
                    "missing_skills": score.missing_skills,
                    "reasoning": score.reasoning,
                    "source": job.source,
                },
            }
        )
        return JobScoreResponse(
            relevance_score=int(saved.relevance_score or score.relevance_score),
            missing_skills=list(saved.ai_analysis.get("missing_skills", [])),
            reasoning=str(saved.ai_analysis.get("reasoning", score.reasoning)),
        )

    def _build_sources(self, client: httpx.AsyncClient, source_names: list[str]):
        registry = {
            "linkedin": LinkedInDiscovery(client),
            "google": GoogleDiscovery(client),
            "wellfound": WellfoundDiscovery(client),
        }
        return [registry[name] for name in source_names if name in registry]

    async def _store_job(self, discovered: DiscoveredJob) -> JobRead:
        ats_type = detect_ats_type(str(discovered.apply_url))
        saved = await self.job_repository.upsert_job(
            {
                "source_id": discovered.source_id,
                "company": discovered.company,
                "title": discovered.title,
                "location": discovered.location,
                "salary_text": discovered.salary_text,
                "apply_url": str(discovered.apply_url),
                "ats_type": ats_type,
                "source": discovered.source,
                "description": discovered.description,
                "posted_at": discovered.posted_at,
                "discovered_at": datetime.now(timezone.utc),
                "relevance_score": None,
                "ai_analysis": {"source": discovered.source, "metadata": discovered.metadata},
            }
        )
        return JobRead.model_validate(saved)
