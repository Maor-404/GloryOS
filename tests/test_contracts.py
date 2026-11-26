"""Automated contract validation tests across all GloryOS JSON Schemas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gloryos_core.cli import main
from gloryos_core.contracts import (
    KNOWN_CONTRACTS,
    ContractValidationError,
    default_repo_root,
    load_document,
    load_schema,
    validate_contract,
)


@pytest.mark.parametrize("contract_name", sorted(KNOWN_CONTRACTS))
def test_all_schemas_are_valid_draft_2020_12(contract_name: str) -> None:
    schema = load_schema(contract_name)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_base_distro_manifest_conforms_to_schema() -> None:
    manifest_path = default_repo_root() / "configs" / "distro" / "gloryos-base.yaml"
    manifest = load_document(manifest_path)
    validate_contract("distro-manifest", manifest)
    assert main(["validate", "--contract", "distro-manifest", str(manifest_path)]) == 0


def test_distro_manifest_rejects_online_account_requirement() -> None:
    manifest_path = default_repo_root() / "configs" / "distro" / "gloryos-base.yaml"
    manifest = load_document(manifest_path)
    manifest["boot"]["require_online_account"] = True
    with pytest.raises(ContractValidationError, match="require_online_account"):
        validate_contract("distro-manifest", manifest)


def test_executable_inspection_blocks_installer_auto_execution(tmp_path: Path) -> None:
    valid_installer_report: dict[str, Any] = {
        "schema_version": "1.0",
        "file_path": str(tmp_path / "setup_app.exe"),
        "sha256": "a" * 64,
        "format": "pe32_plus",
        "architecture": "x86_64",
        "subsystem": "windows_gui",
        "is_installer": True,
        "installer_kind": "inno",
        "auto_execute_allowed": False,
        "frameworks": ["win32"],
        "imported_dlls": ["KERNEL32.dll", "USER32.dll"],
        "compatibility_status": "supported_compatibility",
        "recommended_runtime": "wine",
        "warnings": ["Inno Setup installer requires explicit user confirmation."],
        "blockers": [],
    }
    validate_contract("executable-inspection", valid_installer_report)

    unsafe_installer = dict(valid_installer_report)
    unsafe_installer["auto_execute_allowed"] = True
    with pytest.raises(ContractValidationError, match="auto_execute_allowed"):
        validate_contract("executable-inspection", unsafe_installer)


def test_executable_inspection_enforces_unsupported_runtime_none(tmp_path: Path) -> None:
    unsupported_report: dict[str, Any] = {
        "schema_version": "1.0",
        "file_path": str(tmp_path / "anticheat_game.exe"),
        "sha256": "b" * 64,
        "format": "pe32_plus",
        "architecture": "x86_64",
        "is_installer": False,
        "auto_execute_allowed": False,
        "frameworks": ["directx12"],
        "imported_dlls": ["d3d12.dll"],
        "compatibility_status": "unsupported",
        "recommended_runtime": "proton-umu",
        "warnings": [],
        "blockers": ["kernel_anticheat_detected"],
    }
    with pytest.raises(ContractValidationError, match="recommended_runtime"):
        validate_contract("executable-inspection", unsupported_report)

    unsupported_report["recommended_runtime"] = "none"
    validate_contract("executable-inspection", unsupported_report)


def test_install_plan_enforces_user_authorization_and_sha256() -> None:
    valid_plan: dict[str, Any] = {
        "schema_version": "1.0",
        "package_id": "Notepad++.Notepad++",
        "display_name": "Notepad++",
        "version": "8.7.0",
        "license": "GPL-3.0-or-later",
        "source_ecosystem": "winget",
        "selected_strategy": "winget_via_glorybridge",
        "artifact": {
            "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.7/npp.8.7.Installer.x64.exe",
            "sha256": "0123456789abcdef" * 4,
            "installer_type": "nullsoft",
            "architecture": "x64",
        },
        "target_prefix": "notepad-plus-plus",
        "requires_user_authorization": True,
        "auto_execute": False,
        "summary": "Install Notepad++ (x64 NSIS) into isolated Wine prefix 'notepad-plus-plus'.",
        "warnings": [],
    }
    validate_contract("install-plan", valid_plan)

    unauthorized = dict(valid_plan)
    unauthorized["requires_user_authorization"] = False
    with pytest.raises(ContractValidationError, match="requires_user_authorization"):
        validate_contract("install-plan", unauthorized)

    http_artifact = dict(valid_plan)
    http_artifact["artifact"] = dict(valid_plan["artifact"], url="http://example.com/setup.exe")
    with pytest.raises(ContractValidationError, match="https://"):
        validate_contract("install-plan", http_artifact)


def test_compatibility_profile_schema_validation(tmp_path: Path) -> None:
    profile_yaml = tmp_path / "profile.yaml"
    profile_yaml.write_text(
        """
schema_version: "1.0"
profile_id: "sample-dx11-app"
application_name: "Sample DX11 App"
executable_path: "C:/Program Files/Sample/app.exe"
runtime: "proton-umu"
prefix_name: "sample-dx11"
windows_version: "win10"
display_backend: "xwayland"
enable_ntsync: true
graphics_translation: "dxvk"
isolation:
  expose_host_root_drive: false
  isolated_appdata: true
""".lstrip(),
        encoding="utf-8",
    )
    assert main(["validate", "--contract", "compatibility-profile", str(profile_yaml)]) == 0
