"""Unit tests for non-destructive workspace preflight diagnostics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gloryos_core.cli import main
from gloryos_core.preflight import (
    _detect_qemu_accelerator,
    _find_ovmf_firmware,
    _read_total_ram_gib,
    run_preflight,
)


def test_read_total_ram_gib_parses_meminfo(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal:        8388608 kB\nMemFree:         4194304 kB\n",
        encoding="utf-8",
    )
    assert _read_total_ram_gib(meminfo) == 8.0
    assert _read_total_ram_gib(tmp_path / "missing") == 0.0


def test_detect_qemu_accelerator_falls_back_to_tcg(tmp_path: Path) -> None:
    assert _detect_qemu_accelerator(tmp_path / "nonexistent_kvm") == "tcg"
    fake_kvm = tmp_path / "kvm"
    fake_kvm.write_text("", encoding="utf-8")
    fake_kvm.chmod(0o600)
    assert _detect_qemu_accelerator(fake_kvm) == "kvm"


def test_find_ovmf_firmware_resolves_first_existing_candidate(tmp_path: Path) -> None:
    missing = tmp_path / "missing.fd"
    present = tmp_path / "OVMF_CODE_4M.fd"
    present.write_bytes(b"OVMF")
    assert _find_ovmf_firmware((missing, present)) == str(present)
    assert _find_ovmf_firmware((missing,)) is None


def test_run_preflight_rejects_unknown_milestone() -> None:
    with pytest.raises(ValueError, match="Unsupported milestone"):
        run_preflight(milestone="M99")


def test_cli_preflight_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["preflight", "--milestone", "M0", "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["milestone"] == "M0"
    assert payload["architecture"] == "x86_64"
    assert payload["qemu_accelerator"] in {"kvm", "tcg"}
    assert exit_code in {0, 1}
