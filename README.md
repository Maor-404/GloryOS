# GloryOS

> **Linux infrastructure. Windows application compatibility. Open-source freedom.**

GloryOS is an open-source, Ubuntu LTS–based `x86_64` Linux distribution engineered around practical Windows and `.NET` application compatibility on a Wayland-first KDE Plasma 6 desktop — without proprietary backends, mandatory Steam client dependencies, or unnecessary forks of upstream projects.

---

## Core Design Principles

- **Ubuntu LTS Foundation:** Built reproducibly on official Ubuntu LTS packages (`26.04 LTS resolute`, `x86_64`) using APT/dpkg and the upstream Ubuntu kernel (`/dev/ntsync` enabled).
- **KDE Plasma 6 Desktop:** Wayland session (`KWin` + `XWayland`) with lightweight GloryOS branding, file manager integration, and `Glory Control Center`.
- **GloryBridge Compatibility Engine:** Static PE/CLR/installer inspection, isolated Wine 10/11 (`new WoW64`) prefix orchestration, desktop shortcuts, and transparent failure diagnostics. Never auto-executes downloaded installers.
- **Standalone Proton:** Gaming compatibility via Valve's open-source Proton executed through `Open-Wine-Components/umu-launcher` (`umu-run`) — zero Steam client or Steam account required.
- **Dual `.NET` Support:** Portable cross-platform `.NET` assemblies run natively on Microsoft's MIT-licensed Linux `.NET` runtime (`8` / `10` LTS); Windows-bound `WPF` / `WinForms` / `.NET Framework` assemblies route cleanly to isolated Wine environments.
- **APT + WinGet Manifest Adapter:** Native Linux software installs via APT; `microsoft/winget-pkgs` YAML manifests are inspected, checked against native Linux alternatives first, SHA-256 verified, and translated into auditable installation plans requiring explicit user authorization.
- **GloryRebuild:** Static source-repository analyzer and `bubblewrap`-isolated builder for recompiling genuinely portable open-source applications into native `.deb` packages while preserving upstream licenses.

---

## Documentation

| Document | Purpose |
| :--- | :--- |
| [`docs/PREFLIGHT.md`](docs/PREFLIGHT.md) | Environment & hardware inspection, upstream maintenance audit, licensing constraints, and compatibility limitations |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture, subsystem specifications, security invariants, and 9-role JSON Schema contracts |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Ordered milestones (`M0`–`M9`) with strict prerequisites and verification gates |
| [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) | Third-party component attributions and SPDX license ledger |
| [`schemas/`](schemas/) | Draft 2020-12 JSON Schemas enforcing inter-subsystem integration contracts |

---

## Quickstart (Isolated Workspace / VM)

```bash
# 1. Provision isolated workspace tools and .venv
#    (Set GLORYOS_SKIP_APT=1 on bare-metal hosts to skip APT package installation)
make setup

# 2. Run static analysis, strict type-checking, contract validation, unit tests,
#    dependency vulnerability audit, and resource preflight
make check

# 3. Inspect workspace readiness as JSON
.venv/bin/gloryos preflight --milestone M1 --json
```

---

## Current Status

- **Completed:** `M0` — Architecture, upstream/license preflight, JSON Schema contracts, `gloryos-core` validator & preflight CLI, CI pipeline, and automated verification suite.
- **Next Milestone:** `M1` — Reproducible bootable Ubuntu LTS UEFI image (`mmdebstrap` + `xorriso` + headless `QEMU/OVMF` serial boot verification).

---

## License

Original GloryOS code and specifications are licensed under the **GNU General Public License v3.0 or later** ([`LICENSE`](LICENSE)). Upstream packages retain their respective open-source licenses; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).