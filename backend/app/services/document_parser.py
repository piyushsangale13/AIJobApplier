from pathlib import Path

from docx import Document
from pypdf import PdfReader


class DocumentParser:
    async def extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(file_path)
        if suffix == ".docx":
            return self._extract_docx(file_path)
        raise ValueError(f"Unsupported resume format: {suffix}")

    def _extract_pdf(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    def _extract_docx(self, file_path: Path) -> str:
        document = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
