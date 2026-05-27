from textwrap import dedent

from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.resume import ResumeParsedData


logger = get_logger(__name__)


class JobScoreResult(BaseModel):
    relevance_score: int = Field(ge=1, le=100)
    missing_skills: list[str] = Field(default_factory=list)
    reasoning: str


class CoverLetterResult(BaseModel):
    cover_letter: str


class QuestionAnswerResult(BaseModel):
    answer: str
    confidence: str


class TailoredResumeResult(BaseModel):
    tailored_resume: str
    key_changes: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)


class AIService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def parse_resume(self, raw_text: str) -> ResumeParsedData:
        if not self.client:
            logger.warning("ai.parse_resume.mocked", reason="missing_openai_api_key")
            return self._fallback_resume_parse(raw_text)

        prompt = dedent(
            """
            Extract structured information from this resume.
            Be faithful to the source text.
            Do not invent experience or claims.
            """
        ).strip()

        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            text_format=ResumeParsedData,
        )
        return response.output_parsed

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def score_job(self, resume_data: dict, job_description: str) -> JobScoreResult:
        if not self.client:
            return JobScoreResult(
                relevance_score=70,
                missing_skills=[],
                reasoning="Fallback score used because OpenAI API key is not configured.",
            )

        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "Score job relevance based only on provided resume data. Stay truthful.",
                },
                {
                    "role": "user",
                    "content": f"Resume: {resume_data}\n\nJob description:\n{job_description}",
                },
            ],
            text_format=JobScoreResult,
        )
        return response.output_parsed

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def generate_cover_letter(self, resume_data: dict, job_description: str) -> str:
        if not self.client:
            return "OpenAI API key not configured. Cover letter generation is unavailable."

        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "Write a concise truthful cover letter using only the supplied resume context.",
                },
                {
                    "role": "user",
                    "content": f"Resume: {resume_data}\n\nJob description:\n{job_description}",
                },
            ],
            text_format=CoverLetterResult,
        )
        return response.output_parsed.cover_letter

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def answer_application_question(self, resume_data: dict, question: str) -> QuestionAnswerResult:
        if not self.client:
            return QuestionAnswerResult(
                answer="Manual review needed because OpenAI API key is not configured.",
                confidence="low",
            )

        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "Answer application questions truthfully from the supplied resume context only.",
                },
                {"role": "user", "content": f"Resume: {resume_data}\n\nQuestion: {question}"},
            ],
            text_format=QuestionAnswerResult,
        )
        return response.output_parsed

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def tailor_resume(self, resume_data: dict, job_description: str) -> TailoredResumeResult:
        if not self.client:
            return TailoredResumeResult(
                tailored_resume="OpenAI API key not configured. Resume tailoring is unavailable.",
                key_changes=[],
                matched_keywords=[],
            )

        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": dedent("""
                        Tailor the candidate's resume for the given job description.
                        Rules:
                        - Reorder and reword bullet points to highlight the most relevant experience first
                        - Naturally weave in keywords from the job description where they genuinely apply
                        - Do NOT invent experience, skills, or qualifications not present in the resume
                        - Return the full tailored resume as clean markdown
                        - List the specific changes made and the keywords matched
                    """).strip(),
                },
                {
                    "role": "user",
                    "content": f"Resume data:\n{resume_data}\n\nJob description:\n{job_description}",
                },
            ],
            text_format=TailoredResumeResult,
        )
        return response.output_parsed

    def _fallback_resume_parse(self, raw_text: str) -> ResumeParsedData:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        email = next((token for token in raw_text.split() if "@" in token and "." in token), None)
        skills = [
            keyword
            for keyword in ["Python", "JavaScript", "TypeScript", "React", "FastAPI", "SQL", "PostgreSQL"]
            if keyword.lower() in raw_text.lower()
        ]
        return ResumeParsedData(
            name=lines[0] if lines else None,
            email=email,
            skills=skills,
            experience=lines[1:5],
            preferred_roles=[],
            projects=[],
            education=[],
            keywords=skills,
            summary=lines[1] if len(lines) > 1 else None,
        )
