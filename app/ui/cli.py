from __future__ import annotations

import argparse
from pathlib import Path

from app.export.report import render_markdown
from app.interpretation_engine.engine import InterpretationEngine
from app.models import Category, PatientProfile, Sex
from app.ocr.service import OCRService
from app.reference_database.repository import ReferenceRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analizador académico de laboratorio")
    parser.add_argument("--input", required=True, help="Ruta de entrada (.txt OCR o .pdf)")
    parser.add_argument("--edad", type=int, required=True)
    parser.add_argument("--sexo", choices=["M", "F"], required=True)
    parser.add_argument("--categoria", choices=["nino", "adulto", "adulto_mayor"], required=True)
    parser.add_argument("--erc", action="store_true", help="Indica presencia de ERC")
    parser.add_argument("--etapa-erc", type=int, choices=[1, 2, 3, 4, 5])
    parser.add_argument("--output", default="reporte.md")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    profile = PatientProfile(
        age=args.edad,
        sex=Sex(args.sexo),
        category=Category(args.categoria),
        has_ckd=args.erc,
        ckd_stage=args.etapa_erc,
    )

    repository = ReferenceRepository()
    ocr = OCRService(repository)
    extracted = ocr.extract(args.input)

    engine = InterpretationEngine(repository)
    report = engine.analyze(profile, extracted)
    markdown = render_markdown(report)

    Path(args.output).write_text(markdown, encoding="utf-8")
    print(f"Reporte generado en {args.output}")


if __name__ == "__main__":
    main()
