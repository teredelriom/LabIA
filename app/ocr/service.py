from __future__ import annotations

import re
from pathlib import Path
from typing import List

from app.models import LabResult
from app.reference_database.repository import ReferenceRepository


class OCRService:
    """
    Implementación base para entorno académico.
    - TXT: parseo directo de contenido OCR preextraído.
    - PDF: intenta extracción por texto embebido (pdfplumber) y fallback OCR (pytesseract+pdf2image).
    """

    pattern = re.compile(
        r"([A-Za-zÁÉÍÓÚáéíóúñÑ0-9]+)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*([%A-Za-z/µ0-9.^-]+)"
    )

    def __init__(self, repository: ReferenceRepository):
        self.repository = repository

    def extract(self, path: str) -> List[LabResult]:
        suffix = Path(path).suffix.lower()
        if suffix == ".txt":
            return self.extract_from_text_file(path)
        if suffix == ".pdf":
            return self.extract_from_pdf(path)
        raise ValueError(f"Formato no soportado: {suffix}. Usa .txt o .pdf")

    def extract_from_text_file(self, path: str) -> List[LabResult]:
        content = Path(path).read_text(encoding="utf-8")
        return self.parse_text(content)

    def extract_from_pdf(self, path: str) -> List[LabResult]:
        text = self._extract_text_pdfplumber(path)
        if not text.strip():
            text = self._extract_text_tesseract(path)
        return self.parse_text(text)

    def parse_text(self, text: str) -> List[LabResult]:
        results: List[LabResult] = []
        for raw_name, raw_value, raw_unit in self.pattern.findall(text):
            rule = self.repository.find_rule(raw_name)
            parameter_name = rule.parameter if rule else raw_name
            results.append(
                LabResult(
                    parameter=parameter_name,
                    value=float(raw_value),
                    unit=raw_unit,
                )
            )
        return results

    @staticmethod
    def _extract_text_pdfplumber(path: str) -> str:
        try:
            import pdfplumber  # type: ignore
        except ImportError:
            return ""

        pages: List[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)

    @staticmethod
    def _extract_text_tesseract(path: str) -> str:
        try:
            import pytesseract  # type: ignore
            from pdf2image import convert_from_path  # type: ignore
        except ImportError:
            return ""

        pages = convert_from_path(path)
        chunks: List[str] = []
        for page in pages:
            chunks.append(pytesseract.image_to_string(page, lang="spa+eng"))
        return "\n".join(chunks)
