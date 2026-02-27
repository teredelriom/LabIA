from __future__ import annotations

from html import escape

from app.models import AnalysisReport


def render_html(report: AnalysisReport) -> str:
    rows = []
    for item in report.classified:
        ref = item.reference_range
        rows.append(
            "<tr>"
            f"<td>{escape(item.parameter)}</td>"
            f"<td>{item.normalized_value:.2f} {escape(item.normalized_unit)}</td>"
            f"<td>{ref.low}-{ref.high} {escape(ref.unit)}</td>"
            f"<td>{escape(item.level.value)}</td>"
            f"<td>{escape(item.severity.value)}</td>"
            f"<td>{escape(item.note)}</td>"
            "</tr>"
        )

    findings = "".join(
        f"<li><strong>{escape(f.title)}:</strong> {escape(f.interpretation)}"
        f"<br><small>Evidencia: {escape(', '.join(f.evidence))}</small></li>"
        for f in report.findings
    ) or "<li>Sin patrones sindromáticos relevantes.</li>"

    unmapped = "".join(
        f"<li>{escape(name)} (requiere vinculación manual)</li>"
        for name in sorted(set(report.unmapped_parameters))
    ) or "<li>Sin parámetros pendientes de mapeo.</li>"

    alerts = "".join(f"<li>🔴 {escape(a)}</li>" for a in report.alerts) or "<li>Sin valores críticos.</li>"

    return f"""<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Informe académico de laboratorio</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #f7f9fc; color: #1f2937; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
    th {{ background: #f3f4f6; }}
    .warning {{ color: #b91c1c; font-weight: 600; }}
    .muted {{ color: #6b7280; }}
  </style>
</head>
<body>
  <h1>Informe académico de laboratorio</h1>
  <p class='muted'><strong>Paciente:</strong> {report.patient.age} años | {escape(report.patient.sex.value)} | {escape(report.patient.category.value)}</p>

  <div class='card'>
    <h2>Tabla interpretativa</h2>
    <table>
      <thead>
        <tr><th>Parámetro</th><th>Resultado</th><th>Rango</th><th>Estado</th><th>Severidad</th><th>Nota</th></tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>

  <div class='card'>
    <h2>Patrones detectados</h2>
    <ul>{findings}</ul>
  </div>

  <div class='card'>
    <h2>Parámetros no reconocidos</h2>
    <ul>{unmapped}</ul>
  </div>

  <div class='card'>
    <h2>Alertas</h2>
    <ul class='warning'>{alerts}</ul>
  </div>

  <div class='card'>
    <h2>Conclusión académica</h2>
    <p>{escape(report.summary)}</p>
    <p class='muted'>Uso exclusivamente académico. No reemplaza evaluación médica ni define diagnósticos definitivos.</p>
  </div>
</body>
</html>
"""
