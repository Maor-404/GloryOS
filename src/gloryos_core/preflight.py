"""Non-destructive workspace resource and toolchain preflight checks."""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

QemuAccelerator = Literal["kvm", "tcg"]

MILESTONE_TOOLS: dict[str, tuple[str, ...]] = {
    "M0": (
        "git",
        "python3",
        "dpkg-deb",
        "shellcheck",
    ),
    "M1": (
        "git",
        "python3",
        "dpkg-deb",
        "shellcheck",
        "mmdebstrap",
        "mksquashfs",
        "xorriso",
        "grub-mkstandalone",
        "mformat",
        "qemu-system-x86_64",
        "qemu-img",
    ),
    "M3": (
        "git",
        "python3",
        "dpkg-deb",
        "shellcheck",
        "mmdebstrap",
        "mksquashfs",
        "xorriso",
        "grub-mkstandalone",
        "mformat",
        "qemu-system-x86_64",
        "qemu-img",
        "bwrap",
        "dotnet",
    ),
}

OVMF_CANDIDATES: tuple[Path, ...] = (
    Path("/usr/share/OVMF/OVMF_CODE_4M.fd"),
    Path("/usr/share/OVMF/OVMF_CODE.fd"),
    Path("/usr/share/edk2/ovmf/OVMF_CODE.fd"),
)

MIN_DISK_GIB_IMAGE_BUILD = 15.0
MIN_RAM_GIB_IMAGE_BUILD = 4.0


@dataclass(frozen=True)
class PreflightReport:
    """Structured snapshot of workspace readiness for a target milestone."""

    milestone: str
    ready: bool
    architecture: str
    cpu_count: int
    total_ram_gib: float
    free_disk_gib: float
    qemu_accelerator: QemuAccelerator
    ovmf_firmware: str | None
    missing_tools: list[str]
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize report to a JSON-compatible dictionary."""
        return asdict(self)


def _read_total_ram_gib(meminfo_path: Path = Path("/proc/meminfo")) -> float:
    if not meminfo_path.is_file():
        return 0.0
    for line in meminfo_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                kib = int(parts[1])
                return round(kib / (1024.0 * 1024.0), 2)
    return 0.0


def _detect_qemu_accelerator(kvm_device: Path = Path("/dev/kvm")) -> QemuAccelerator:
    if kvm_device.exists() and os.access(kvm_device, os.R_OK | os.W_OK):
        return "kvm"
    return "tcg"


def _find_ovmf_firmware(candidates: tuple[Path, ...] = OVMF_CANDIDATES) -> str | None:
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def run_preflight(
    milestone: str = "M0",
    workspace_path: Path | None = None,
) -> PreflightReport:
    """Inspect workspace resources and installed tools without mutating host state."""
    if milestone not in MILESTONE_TOOLS:
        supported = ", ".join(sorted(MILESTONE_TOOLS))
        msg = f"Unsupported milestone '{milestone}'. Supported: {supported}"
        raise ValueError(msg)

    target_dir = workspace_path if workspace_path is not None else Path.cwd()
    arch = platform.machine()
    cpus = os.cpu_count() or 1
    ram_gib = _read_total_ram_gib()
    disk_free_gib = round(shutil.disk_usage(target_dir).free / (1024.0**3), 2)
    accel = _detect_qemu_accelerator()
    ovmf = _find_ovmf_firmware()

    missing_tools = [tool for tool in MILESTONE_TOOLS[milestone] if shutil.which(tool) is None]

    blockers: list[str] = []
    warnings: list[str] = []

    if arch != "x86_64":
        blockers.append(f"Initial GloryOS target requires x86_64 workspace; detected '{arch}'.")

    if missing_tools:
        blockers.append(f"Missing required CLI tools: {', '.join(missing_tools)}")

    if accel == "tcg":
        warnings.append(
            "/dev/kvm unavailable; QEMU tests must use software TCG acceleration (-accel tcg)."
        )

    if milestone in {"M1", "M3"}:
        if ovmf is None:
            blockers.append("UEFI firmware (OVMF) not found; install package 'ovmf'.")
        if disk_free_gib < MIN_DISK_GIB_IMAGE_BUILD:
            blockers.append(
                f"At least {MIN_DISK_GIB_IMAGE_BUILD} GiB free disk required; "
                f"found {disk_free_gib} GiB."
            )
        if 0.0 < ram_gib < MIN_RAM_GIB_IMAGE_BUILD:
            blockers.append(
                f"At least {MIN_RAM_GIB_IMAGE_BUILD} GiB RAM required; found {ram_gib} GiB."
            )

    return PreflightReport(
        milestone=milestone,
        ready=len(blockers) == 0,
        architecture=arch,
        cpu_count=cpus,
        total_ram_gib=ram_gib,
        free_disk_gib=disk_free_gib,
        qemu_accelerator=accel,
        ovmf_firmware=ovmf,
        missing_tools=missing_tools,
        blockers=blockers,
        warnings=warnings,
    )
