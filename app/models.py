from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Sex(str, Enum):
    M = "M"
    F = "F"


class Category(str, Enum):
    PEDIATRIC = "nino"
    ADULT = "adulto"
    ELDERLY = "adulto_mayor"


class Level(str, Enum):
    LOW = "bajo"
    NORMAL = "normal"
    HIGH = "alto"
    CRITICALLY_LOW = "criticamente_bajo"
    CRITICALLY_HIGH = "criticamente_alto"


class Severity(str, Enum):
    NONE = "ninguna"
    MILD = "leve"
    MODERATE = "moderado"
    SEVERE = "severo"


@dataclass
class PatientProfile:
    age: int
    sex: Sex
    category: Category
    has_ckd: bool = False
    ckd_stage: Optional[int] = None


@dataclass
class LabResult:
    parameter: str
    value: float
    unit: str


@dataclass
class Range:
    low: float
    high: float
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None
    unit: str = ""


@dataclass
class ReferenceRule:
    parameter: str
    aliases: List[str]
    standard_unit: str
    conversion: Dict[str, float]
    by_category: Dict[str, Range]
    by_sex: Dict[str, Range] = field(default_factory=dict)
    ckd_overrides: Dict[str, Dict[str, Range]] = field(default_factory=dict)
    source: str = ""
    updated_at: str = ""


@dataclass
class ClassifiedResult:
    parameter: str
    value: float
    unit: str
    normalized_value: float
    normalized_unit: str
    reference_range: Range
    level: Level
    severity: Severity
    note: str = ""


@dataclass
class SyndromeFinding:
    title: str
    evidence: List[str]
    interpretation: str


@dataclass
class AnalysisReport:
    patient: PatientProfile
    classified: List[ClassifiedResult]
    findings: List[SyndromeFinding]
    alerts: List[str]
    summary: str
    unmapped_parameters: List[str] = field(default_factory=list)
