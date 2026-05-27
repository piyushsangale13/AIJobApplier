from textwrap import dedent

from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.resume import ResumeParsedData


logger = get_logger(__name__)


class ATSScoreResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    contact_score: int = Field(ge=0, le=15)
    skills_score: int = Field(ge=0, le=20)
    experience_score: int = Field(ge=0, le=25)
    education_score: int = Field(ge=0, le=15)
    keywords_score: int = Field(ge=0, le=15)
    formatting_score: int = Field(ge=0, le=10)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ResumeParseAndScoreResult(BaseModel):
    """Combined output so a single AI call handles both parsing and ATS scoring."""

    # ── Parsed resume fields ──────────────────────────────────────────────────
    name: str | None = None
    email: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    preferred_roles: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    summary: str | None = None

    # ── ATS score fields ──────────────────────────────────────────────────────
    ats_contact_score: int = Field(ge=0, le=15)
    ats_skills_score: int = Field(ge=0, le=20)
    ats_experience_score: int = Field(ge=0, le=25)
    ats_education_score: int = Field(ge=0, le=15)
    ats_keywords_score: int = Field(ge=0, le=15)
    ats_formatting_score: int = Field(ge=0, le=10)
    ats_issues: list[str] = Field(default_factory=list)
    ats_recommendations: list[str] = Field(default_factory=list)

    def split(self) -> tuple[ResumeParsedData, ATSScoreResult]:
        parsed = ResumeParsedData(
            name=self.name,
            email=self.email,
            skills=self.skills,
            experience=self.experience,
            preferred_roles=self.preferred_roles,
            projects=self.projects,
            education=self.education,
            keywords=self.keywords,
            summary=self.summary,
        )
        computed = (
            self.ats_contact_score + self.ats_skills_score + self.ats_experience_score
            + self.ats_education_score + self.ats_keywords_score + self.ats_formatting_score
        )
        ats = ATSScoreResult(
            overall_score=min(computed, 100),
            contact_score=self.ats_contact_score,
            skills_score=self.ats_skills_score,
            experience_score=self.ats_experience_score,
            education_score=self.ats_education_score,
            keywords_score=self.ats_keywords_score,
            formatting_score=self.ats_formatting_score,
            issues=self.ats_issues,
            recommendations=self.ats_recommendations,
        )
        return parsed, ats


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
    async def parse_and_score_resume(self, raw_text: str) -> tuple[ResumeParsedData, ATSScoreResult]:
        if not self.client:
            logger.warning("ai.parse_and_score_resume.mocked", reason="missing_openai_api_key")
            parsed = self._fallback_resume_parse(raw_text)
            ats = ATSScoreResult(
                overall_score=0,
                contact_score=0, skills_score=0, experience_score=0,
                education_score=0, keywords_score=0, formatting_score=0,
                issues=["OpenAI API key not configured — ATS scoring unavailable."],
                recommendations=[],
            )
            return parsed, ats

        prompt = dedent("""
            You are an expert resume analyst and ATS (Applicant Tracking System) evaluator.
            Given a resume, do two things in a single pass:

            ── PART 1: Extract structured data ──────────────────────────────────
            Be faithful to the source text. Do not invent experience or claims.
            • name            – full name as written
            • email           – email address (null if absent)
            • skills          – all technical and domain skills mentioned
            • experience      – each role as one string: "Title at Company (Start–End): key responsibilities"
            • preferred_roles – job titles the candidate is targeting (infer from objective/summary if present)
            • projects        – each project as one string with tech stack if mentioned
            • education       – each entry: "Degree, Institution, Year"
            • keywords        – industry/role keywords suitable for job matching
            • summary         – 2-3 sentence professional summary (use stated objective, else synthesise)

            ── PART 2: ATS compatibility score ──────────────────────────────────
            Be strict and realistic. Most resumes score 40–75; only exceptional ones exceed 85.
            Prefix every ATS field with "ats_" to avoid name collisions.

            ats_contact_score (0–15)
              +5  full name present
              +5  professional email present
              +3  phone number present
              +2  LinkedIn / GitHub / portfolio URL present

            ats_skills_score (0–20)
              +5  dedicated skills section with clear header
              +8  10 or more specific technical/domain skills listed
              +4  mix of hard skills (tools, languages) and soft skills
              +3  skills use standard industry terminology

            ats_experience_score (0–25)
              +8  each role has job title, company name, and employment dates
              +7  bullet points start with strong action verbs (Led, Built, Reduced…)
              +6  at least one quantified achievement (number, %, $, or time saved)
              +4  2+ years of total relevant experience described

            ats_education_score (0–15)
              +8  degree name and institution clearly stated
              +4  graduation year included
              +3  certifications, coursework, or honours mentioned

            ats_keywords_score (0–15)
              +6  industry-standard keywords present (REST API, CI/CD, Agile…)
              +5  technical terminology matches common job descriptions for this field
              +4  no spelling or obvious grammar errors detected

            ats_formatting_score (0–10)
              +3  standard section headers used (Experience, Education, Skills…)
              +3  no tables, multi-column layouts, or complex graphics
              +2  no critical info buried in headers/footers
              +2  consistent date format and spacing throughout

            ats_issues         – list of specific problems hurting the score
            ats_recommendations – top 3 highest-impact improvements, each actionable
        """).strip()

        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            text_format=ResumeParseAndScoreResult,
        )
        return response.output_parsed.split()

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
