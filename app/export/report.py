from __future__ import annotations

from typing import List

from app.models import AnalysisReport


def render_markdown(report: AnalysisReport) -> str:
    lines: List[str] = []
    lines.append("# Informe académico de laboratorio")
    lines.append("")
    lines.append(
        f"**Paciente:** {report.patient.age} años | {report.patient.sex.value} | {report.patient.category.value}"
    )
    lines.append("")
    lines.append("## Tabla interpretativa")
    lines.append("")
    lines.append("| Parámetro | Resultado | Rango | Estado | Severidad | Nota |")
    lines.append("|---|---:|---|---|---|---|")

    for item in report.classified:
        ref = item.reference_range
        range_txt = f"{ref.low}-{ref.high} {ref.unit}"
        result_txt = f"{item.normalized_value:.2f} {item.normalized_unit}"
        lines.append(
            f"| {item.parameter} | {result_txt} | {range_txt} | {item.level.value} | {item.severity.value} | {item.note} |"
        )

    lines.append("")
    lines.append("## Patrones detectados")
    if not report.findings:
        lines.append("- Sin patrones sindromáticos relevantes.")
    else:
        for finding in report.findings:
            lines.append(f"- **{finding.title}**: {finding.interpretation}")
            lines.append(f"  - Evidencia: {', '.join(finding.evidence)}")

    lines.append("")

    lines.append("")
    lines.append("## Parámetros no reconocidos")
    if not report.unmapped_parameters:
        lines.append("- Sin parámetros pendientes de mapeo.")
    else:
        for name in sorted(set(report.unmapped_parameters)):
            lines.append(f"- {name} (requiere vinculación manual)")

    lines.append("## Alertas")
    if not report.alerts:
        lines.append("- Sin valores críticos.")
    else:
        for alert in report.alerts:
            lines.append(f"- 🔴 {alert}")

    lines.append("")
    lines.append("## Conclusión académica")
    lines.append(report.summary)
    return "\n".join(lines)
