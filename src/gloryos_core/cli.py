"""Command-line entrypoint for GloryOS preflight and contract validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gloryos_core.contracts import (
    KNOWN_CONTRACTS,
    ContractValidationError,
    load_document,
    validate_contract,
)
from gloryos_core.preflight import MILESTONE_TOOLS, run_preflight


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gloryos",
        description="GloryOS developer preflight and contract validation CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight_cmd = subparsers.add_parser(
        "preflight",
        help="Run non-destructive workspace resource and toolchain checks.",
    )
    preflight_cmd.add_argument(
        "--milestone",
        choices=sorted(MILESTONE_TOOLS),
        default="M0",
        help="Target milestone toolset to verify (default: M0).",
    )
    preflight_cmd.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit machine-readable JSON output.",
    )

    validate_cmd = subparsers.add_parser(
        "validate",
        help="Validate a YAML or JSON file against a GloryOS schema contract.",
    )
    validate_cmd.add_argument(
        "--contract",
        choices=sorted(KNOWN_CONTRACTS),
        required=True,
        help="Contract schema name.",
    )
    validate_cmd.add_argument(
        "path",
        type=Path,
        help="Path to YAML or JSON document.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the GloryOS CLI and return a POSIX exit status."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "preflight":
        report = run_preflight(milestone=args.milestone)
        if args.as_json:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        else:
            status = "READY" if report.ready else "BLOCKED"
            print(f"[GloryOS Preflight] Milestone={report.milestone} Status={status}")
            print(
                f"  Arch={report.architecture} CPUs={report.cpu_count} "
                f"RAM={report.total_ram_gib}GiB FreeDisk={report.free_disk_gib}GiB "
                f"QEMU={report.qemu_accelerator} OVMF={report.ovmf_firmware or 'missing'}"
            )
            for warning in report.warnings:
                print(f"  WARN: {warning}")
            for blocker in report.blockers:
                print(f"  BLOCKER: {blocker}", file=sys.stderr)
        return 0 if report.ready else 1

    if args.command == "validate":
        doc_path: Path = args.path
        try:
            document = load_document(doc_path)
            validate_contract(args.contract, document)
        except (OSError, ValueError, ContractValidationError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(f"OK: '{doc_path}' conforms to contract '{args.contract}'.")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
