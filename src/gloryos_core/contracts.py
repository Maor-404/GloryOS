"""JSON Schema contract loading and validation for GloryOS subsystems."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

KNOWN_CONTRACTS: frozenset[str] = frozenset(
    {
        "distro-manifest",
        "executable-inspection",
        "compatibility-profile",
        "install-plan",
    }
)


class ContractValidationError(ValueError):
    """Raised when a document violates a GloryOS JSON Schema contract."""

    def __init__(self, contract_name: str, issues: list[str]) -> None:
        self.contract_name = contract_name
        self.issues = issues
        joined = "; ".join(issues)
        super().__init__(f"Contract '{contract_name}' validation failed: {joined}")


def default_repo_root() -> Path:
    """Resolve the repository root relative to the source tree."""
    return Path(__file__).resolve().parents[2]


def load_schema(contract_name: str, schemas_dir: Path | None = None) -> dict[str, Any]:
    """Load and meta-validate a named GloryOS JSON Schema."""
    if contract_name not in KNOWN_CONTRACTS:
        valid = ", ".join(sorted(KNOWN_CONTRACTS))
        msg = f"Unknown contract '{contract_name}'. Expected one of: {valid}"
        raise ValueError(msg)

    base_dir = schemas_dir if schemas_dir is not None else default_repo_root() / "schemas"
    schema_path = base_dir / f"{contract_name}.schema.json"
    if not schema_path.is_file():
        msg = f"Schema file not found: {schema_path}"
        raise FileNotFoundError(msg)

    raw: Any = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Schema root must be a JSON object: {schema_path}"
        raise TypeError(msg)

    Draft202012Validator.check_schema(raw)
    return raw


def load_document(path: Path) -> dict[str, Any]:
    """Safely load a YAML or JSON mapping document from disk."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        parsed: Any = json.loads(text)
    else:
        parsed = yaml.safe_load(text)

    if not isinstance(parsed, dict):
        msg = f"Document root in '{path}' must be a mapping/object"
        raise ValueError(msg)
    return parsed


def validate_contract(
    contract_name: str,
    document: dict[str, Any],
    schemas_dir: Path | None = None,
) -> None:
    """Validate a parsed document against a named GloryOS JSON Schema contract."""
    schema = load_schema(contract_name, schemas_dir=schemas_dir)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda err: list(err.absolute_path))
    if errors:
        issues: list[str] = []
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "<root>"
            issues.append(f"{location}: {error.message}")
        raise ContractValidationError(contract_name, issues)
