from __future__ import annotations

from app.models import LabResult, PatientProfile, Range, ReferenceRule


class NormalizationError(ValueError):
    pass


class LabNormalizer:
    def normalize(self, result: LabResult, rule: ReferenceRule) -> LabResult:
        multiplier = 1.0
        if result.unit != rule.standard_unit:
            if result.unit not in rule.conversion:
                raise NormalizationError(
                    f"No existe conversión para {result.parameter} de {result.unit} a {rule.standard_unit}."
                )
            multiplier = rule.conversion[result.unit]

        normalized_value = result.value * multiplier
        self._coherence_check(rule.parameter, normalized_value, rule.standard_unit)
        return LabResult(parameter=rule.parameter, value=normalized_value, unit=rule.standard_unit)

    @staticmethod
    def pick_range(rule: ReferenceRule, patient: PatientProfile) -> Range:
        if patient.has_ckd and patient.ckd_stage:
            stage = str(patient.ckd_stage)
            if stage in rule.ckd_overrides and patient.category.value in rule.ckd_overrides[stage]:
                return rule.ckd_overrides[stage][patient.category.value]

        sex_key = patient.sex.value.lower()
        if sex_key in rule.by_sex:
            return rule.by_sex[sex_key]

        if patient.category.value in rule.by_category:
            return rule.by_category[patient.category.value]

        raise NormalizationError(
            f"No hay rango definido para {rule.parameter} en {patient.category.value}."
        )

    @staticmethod
    def _coherence_check(parameter: str, value: float, unit: str) -> None:
        key = parameter.lower()
        if key in {"sodio", "na"} and value < 90:
            raise NormalizationError(
                f"Valor incoherente para sodio: {value} {unit}. Revisar OCR o unidades."
            )
        if key in {"hemoglobina", "hb", "hgb"} and value < 2:
            raise NormalizationError(
                f"Valor incoherente para hemoglobina: {value} {unit}."
            )
