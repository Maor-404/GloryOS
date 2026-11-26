# Third-Party Components and License Notices

GloryOS builds upon established open-source projects and respects all upstream licenses, copyright attributions, and source-availability obligations.

Original GloryOS components in this repository are licensed under **GNU General Public License v3.0 or later (`GPL-3.0-or-later`)** unless explicitly noted otherwise in a component's subdirectory.

---

## 1. M0 Workspace & Runtime Python Dependencies

| Component | Upstream Repository | SPDX License | Role in GloryOS |
| :--- | :--- | :--- | :--- |
| `PyYAML` | https://github.com/yaml/pyyaml | `MIT` | Parsing declarative GloryOS distro manifests, compatibility profiles, and WinGet YAML manifests |
| `jsonschema` | https://github.com/python-jsonschema/jsonschema | `MIT` | Validating inter-subsystem JSON Schema contracts |
| `pefile` | https://github.com/erocarrera/pefile | `MIT` | Static PE32/PE32+ executable, import table, and CLR header inspection (M3/M4) |
| `pytest` | https://github.com/pytest-dev/pytest | `MIT` | Automated unit and integration test runner (dev) |
| `ruff` | https://github.com/astral-sh/ruff | `MIT` | Static analysis and formatting for Python code (dev) |
| `mypy` | https://github.com/python/mypy | `MIT` | Strict static type checking for Python code (dev) |
| `pip-audit` | https://github.com/pypa/pip-audit | `Apache-2.0` | Dependency vulnerability auditing against OSV/PyPA advisories (dev) |

---

## 2. Workspace Build, Packaging, and Virtualization Tooling (APT)

Installed inside isolated development workspaces/VMs for image assembly, UEFI testing, and static analysis (not modified or forked by GloryOS):

| Component | Upstream Project | SPDX License | Role in GloryOS |
| :--- | :--- | :--- | :--- |
| `mmdebstrap` / `debootstrap` | Debian Project | `MIT` / `MIT-style` | Reproducible Ubuntu rootfs bootstrapping |
| `squashfs-tools` | https://github.com/plougher/squashfs-tools | `GPL-2.0-or-later` | Live filesystem SquashFS image generation |
| `xorriso` (`libisoburn`) | GNU Xorriso | `GPL-3.0-or-later` | Bootable ISO 9660 + El Torito UEFI image creation |
| `grub-efi-amd64-bin` | GNU GRUB | `GPL-3.0-or-later` | x86_64 UEFI bootloader (`BOOTX64.EFI`) |
| `qemu-system-x86` / `qemu-utils` | https://www.qemu.org | `GPL-2.0-only` | Isolated x86_64 VM boot & installation testing |
| `ovmf` (EDK2) | TianoCore EDK II | `BSD-2-Clause-Patent` | UEFI firmware for QEMU virtual machine testing |
| `bubblewrap` | https://github.com/containers/bubblewrap | `LGPL-2.0-or-later` | Unprivileged namespace sandboxing for `GloryRebuild` and build tasks |
| `debhelper` / `dpkg-dev` / `lintian` | Debian Project | `GPL-2.0-or-later` | Native `.deb` packaging and policy linting |
| `shellcheck` | https://github.com/koalaman/shellcheck | `GPL-3.0-or-later` | Static analysis of POSIX/Bash build scripts |

---

## 3. Target Distribution Upstream Components (M1–M9)

When GloryOS produces installable ISO or VM images (starting in M1), the build pipeline automatically generates a complete package manifest (`manifest.packages`) and extracts `/usr/share/doc/*/copyright` notices into `manifest.licenses`.

| Subsystem | Upstream Project | SPDX License(s) | Integration Method & Obligations |
| :--- | :--- | :--- | :--- |
| Base OS & APT | Ubuntu 26.04 LTS (`resolute`) / Debian | Various DFSG / Ubuntu Component Licenses | Unmodified official Ubuntu LTS packages (`main` & `universe`); preserve `/usr/share/doc/*/copyright` and strip Canonical trademark branding where required by Ubuntu Remix/Derivative policy |
| Linux Kernel | Linux Kernel (Ubuntu LTS kernel, `ntsync` module) | `GPL-2.0-only` WITH `Linux-syscall-note` | Unmodified Ubuntu-signed kernel binary packages; provide `apt source` pointers for GPLv2 compliance |
| Desktop & Compositor | KDE Plasma 6, KWin, KDE Frameworks 6, Qt 6 | `GPL-2.0-or-later`, `GPL-3.0-or-later`, `LGPL-2.1-or-later`, `LGPL-3.0-only` | Unmodified upstream packages + GloryOS branding/QML plugins under `GPL-3.0-or-later` |
| System Installer | Calamares | `GPL-3.0-or-later` | Configured via declarative YAML/QML branding modules (`calamares-settings-gloryos`) |
| Windows API Layer | WineHQ (`wine` 10/11+) & Winetricks | `LGPL-2.1-or-later` | Invoked as separate user-space runtime processes inside isolated prefixes; preserve LGPL notices and source links |
| Gaming Compatibility | Valve Proton (`ValveSoftware/Proton`) | Aggregate: `BSD-3-Clause` (Proton scripts), `LGPL-2.1-or-later` (Wine, vkd3d-proton), `Zlib` (DXVK, FAudio) | Independent integration via `umu-launcher`; never bundle proprietary Steam client binaries; preserve per-component notices and corresponding source pointers if pre-bundled |
| Standalone Proton Runner | `Open-Wine-Components/umu-launcher` & Steam Linux Runtime (`sniper`) | `GPL-3.0-only` (`umu-launcher`), `MIT` / `LGPL-2.1-or-later` (`steam-runtime-tools`) | Invoked via CLI (`umu-run`) with zero Steam client dependency |
| Native .NET Runtime | Microsoft .NET Runtime & SDK (`dotnet` 8 / 10 LTS) | `MIT` | Installed via official Ubuntu `main` packages (`dotnet-runtime-10.0`, `dotnet-runtime-8.0`) |
| WinGet Metadata | Microsoft `winget-pkgs` Community Manifests | `MIT` | Read-only YAML manifest parsing & validation; never execute uninspected installer commands without user authorization |
