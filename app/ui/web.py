from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from app.export.report_html import render_html
from app.interpretation_engine.engine import InterpretationEngine
from app.models import Category, PatientProfile, Sex
from app.ocr.service import OCRService
from app.reference_database.repository import ReferenceRepository


FORM_HTML = """<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>LabIA - Dashboard académico</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background:#f7f9fc; }
    .card { background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:16px; max-width:900px; }
    textarea,input,select { width:100%; padding:8px; margin:6px 0 12px; }
    button { background:#2563eb; color:white; border:none; padding:10px 14px; border-radius:6px; cursor:pointer; }
    h1 { margin-top:0; }
  </style>
</head>
<body>
  <div class='card'>
    <h1>LabIA - Estudio clínico estructurado</h1>
    <p><strong>Uso académico:</strong> no reemplaza evaluación médica.</p>
    <form method='post' action='/analyze'>
      <label>Edad</label><input type='number' name='edad' value='67' required>
      <label>Sexo</label>
      <select name='sexo'><option value='M'>M</option><option value='F'>F</option></select>
      <label>Categoría</label>
      <select name='categoria'>
        <option value='adulto'>Adulto</option>
        <option value='nino'>Niño</option>
        <option value='adulto_mayor'>Adulto mayor</option>
      </select>
      <label>ERC</label>
      <select name='erc'><option value='no'>No</option><option value='si'>Sí</option></select>
      <label>Etapa ERC (1-5)</label><input type='number' name='etapa_erc' min='1' max='5'>
      <label>Resultados OCR (texto)</label>
      <textarea name='ocr_text' rows='10'>Hb: 10.2 g/dL
VCM: 73 fL
Creat: 2.8 mg/dL
eGFR: 25 mL/min/1.73m2
Na: 122 mEq/L</textarea>
      <button type='submit'>Analizar</button>
    </form>
  </div>
</body>
</html>"""


class LabHandler(BaseHTTPRequestHandler):
    repo = ReferenceRepository()
    ocr = OCRService(repo)
    engine = InterpretationEngine(repo)

    def _send_html(self, html: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._send_html(FORM_HTML)
            return
        self._send_html("<h1>Not found</h1>", status=404)

    def do_POST(self):  # noqa: N802
        if self.path != "/analyze":
            self._send_html("<h1>Not found</h1>", status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        data = parse_qs(body)

        edad = int(data.get("edad", ["0"])[0])
        sexo = data.get("sexo", ["M"])[0]
        categoria = data.get("categoria", ["adulto"])[0]
        has_ckd = data.get("erc", ["no"])[0] == "si"
        ckd_stage_raw = data.get("etapa_erc", [""])[0].strip()
        ckd_stage = int(ckd_stage_raw) if ckd_stage_raw else None
        ocr_text = data.get("ocr_text", [""])[0]

        profile = PatientProfile(
            age=edad,
            sex=Sex(sexo),
            category=Category(categoria),
            has_ckd=has_ckd,
            ckd_stage=ckd_stage,
        )
        extracted = self.ocr.parse_text(ocr_text)
        report = self.engine.analyze(profile, extracted)
        self._send_html(render_html(report))


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor web HTML para LabIA")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), LabHandler)
    print(f"LabIA web disponible en http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
