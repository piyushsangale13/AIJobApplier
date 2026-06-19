import io

from docx import Document
from pypdf import PdfReader


class DocumentParser:
    async def extract_text(self, content: bytes, suffix: str) -> str:
        if suffix == ".pdf":
            return self._extract_pdf(content)
        if suffix == ".docx":
            return self._extract_docx(content)
        raise ValueError(f"Unsupported resume format: {suffix}")

    def _extract_pdf(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    def _extract_docx(self, content: bytes) -> str:
        document = Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
