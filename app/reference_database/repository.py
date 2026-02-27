from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from app.models import Range, ReferenceRule


class ReferenceRepository:
    def __init__(self, db_path: str = "data/references.json"):
        self.db_path = Path(db_path)
        self.rules = self._load()

    def _load(self) -> Dict[str, ReferenceRule]:
        payload = json.loads(self.db_path.read_text(encoding="utf-8"))
        items: Dict[str, ReferenceRule] = {}
        for item in payload["parameters"]:
            by_category = {
                key: Range(**value)
                for key, value in item.get("by_category", {}).items()
            }
            by_sex = {key: Range(**value) for key, value in item.get("by_sex", {}).items()}
            ckd_overrides = {
                stage: {
                    category: Range(**range_value)
                    for category, range_value in categories.items()
                }
                for stage, categories in item.get("ckd_overrides", {}).items()
            }
            rule = ReferenceRule(
                parameter=item["parameter"],
                aliases=item.get("aliases", []),
                standard_unit=item["standard_unit"],
                conversion=item.get("conversion", {}),
                by_category=by_category,
                by_sex=by_sex,
                ckd_overrides=ckd_overrides,
                source=item.get("source", ""),
                updated_at=item.get("updated_at", ""),
            )
            items[rule.parameter.lower()] = rule
            for alias in rule.aliases:
                items[alias.lower()] = rule
        return items

    def find_rule(self, parameter_name: str) -> ReferenceRule | None:
        return self.rules.get(parameter_name.lower())

    def known_parameters(self) -> List[str]:
        canonical = {rule.parameter for rule in self.rules.values()}
        return sorted(canonical)
