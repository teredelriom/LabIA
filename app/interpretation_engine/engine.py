from __future__ import annotations

from typing import List

from app.lab_parser.normalizer import LabNormalizer, NormalizationError
from app.models import (
    AnalysisReport,
    ClassifiedResult,
    LabResult,
    Level,
    PatientProfile,
    Severity,
    SyndromeFinding,
)
from app.reference_database.repository import ReferenceRepository


class InterpretationEngine:
    def __init__(self, repository: ReferenceRepository):
        self.repository = repository
        self.normalizer = LabNormalizer()

    def analyze(self, patient: PatientProfile, raw_results: List[LabResult]) -> AnalysisReport:
        classified: List[ClassifiedResult] = []
        alerts: List[str] = []
        unmapped: List[str] = []

        for result in raw_results:
            rule = self.repository.find_rule(result.parameter)
            if not rule:
                unmapped.append(result.parameter)
                continue

            try:
                normalized = self.normalizer.normalize(result, rule)
                reference_range = self.normalizer.pick_range(rule, patient)
            except NormalizationError as exc:
                alerts.append(f"{rule.parameter}: {exc}")
                continue
            level, severity = self._classify(normalized.value, reference_range)
            note = self._parametric_note(rule.parameter, level)
            if level in {Level.CRITICALLY_HIGH, Level.CRITICALLY_LOW}:
                alerts.append(
                    f"{rule.parameter}: valor potencialmente urgente en contexto clínico real."
                )

            classified.append(
                ClassifiedResult(
                    parameter=rule.parameter,
                    value=result.value,
                    unit=result.unit,
                    normalized_value=normalized.value,
                    normalized_unit=normalized.unit,
                    reference_range=reference_range,
                    level=level,
                    severity=severity,
                    note=note,
                )
            )

        findings = self._syndrome_rules(classified)
        summary = self._summary(patient, classified, findings)
        return AnalysisReport(patient, classified, findings, alerts, summary, unmapped)

    def _classify(self, value: float, ref) -> tuple[Level, Severity]:
        if ref.critical_low is not None and value <= ref.critical_low:
            return Level.CRITICALLY_LOW, Severity.SEVERE
        if ref.critical_high is not None and value >= ref.critical_high:
            return Level.CRITICALLY_HIGH, Severity.SEVERE
        if value < ref.low:
            delta = (ref.low - value) / max(ref.low, 0.001)
            return Level.LOW, self._severity(delta)
        if value > ref.high:
            delta = (value - ref.high) / max(ref.high, 0.001)
            return Level.HIGH, self._severity(delta)
        return Level.NORMAL, Severity.NONE

    @staticmethod
    def _severity(delta: float) -> Severity:
        if delta < 0.15:
            return Severity.MILD
        if delta < 0.35:
            return Severity.MODERATE
        return Severity.SEVERE

    @staticmethod
    def _parametric_note(parameter: str, level: Level) -> str:
        key = parameter.lower()
        if key == "hemoglobina" and level in {Level.LOW, Level.CRITICALLY_LOW}:
            return "Hallazgo compatible con anemia en evaluación académica."
        if key == "vcm" and level in {Level.LOW, Level.CRITICALLY_LOW}:
            return "VCM bajo sugiere microcitosis."
        if key == "creatinina" and level in {Level.HIGH, Level.CRITICALLY_HIGH}:
            return "Creatinina elevada sugiere disfunción renal."
        if key == "sodio" and level in {Level.LOW, Level.CRITICALLY_LOW}:
            return "Sodio bajo compatible con hiponatremia."
        return ""

    @staticmethod
    def _syndrome_rules(classified: List[ClassifiedResult]) -> List[SyndromeFinding]:
        by_name = {item.parameter.lower(): item for item in classified}
        findings: List[SyndromeFinding] = []

        hb = by_name.get("hemoglobina")
        vcm = by_name.get("vcm")
        if hb and vcm and hb.level in {Level.LOW, Level.CRITICALLY_LOW} and vcm.level in {
            Level.LOW,
            Level.CRITICALLY_LOW,
        }:
            findings.append(
                SyndromeFinding(
                    title="Patrón de anemia microcítica",
                    evidence=["Hemoglobina baja", "VCM bajo"],
                    interpretation="Probable ferropenia en contexto académico.",
                )
            )

        leu = by_name.get("leucocitos")
        neu = by_name.get("neutrofilos")
        if leu and neu and leu.level in {Level.HIGH, Level.CRITICALLY_HIGH} and neu.level in {
            Level.HIGH,
            Level.CRITICALLY_HIGH,
        }:
            findings.append(
                SyndromeFinding(
                    title="Leucocitosis con neutrofilia",
                    evidence=["Leucocitos altos", "Neutrófilos altos"],
                    interpretation="Probable infección bacteriana (hipótesis de estudio).",
                )
            )

        ast = by_name.get("ast")
        alt = by_name.get("alt")
        if ast and alt and ast.level in {Level.HIGH, Level.CRITICALLY_HIGH} and alt.level in {
            Level.HIGH,
            Level.CRITICALLY_HIGH,
        }:
            findings.append(
                SyndromeFinding(
                    title="Patrón hepatocelular",
                    evidence=["AST elevada", "ALT elevada"],
                    interpretation="Sugerente de daño hepatocelular.",
                )
            )

        crea = by_name.get("creatinina")
        egfr = by_name.get("egfr")
        if crea and egfr and crea.level in {Level.HIGH, Level.CRITICALLY_HIGH} and egfr.level in {
            Level.LOW,
            Level.CRITICALLY_LOW,
        }:
            findings.append(
                SyndromeFinding(
                    title="Compromiso renal",
                    evidence=["Creatinina alta", "eGFR bajo"],
                    interpretation="Patrón compatible con enfermedad renal crónica.",
                )
            )

        return findings

    @staticmethod
    def _summary(
        patient: PatientProfile,
        classified: List[ClassifiedResult],
        findings: List[SyndromeFinding],
    ) -> str:
        altered = [c for c in classified if c.level != Level.NORMAL]
        return (
            f"Perfil {patient.category.value} ({patient.sex.value}), "
            f"{len(altered)} parámetros alterados y {len(findings)} patrones detectados. "
            "Uso exclusivamente académico: no reemplaza evaluación médica."
        )
