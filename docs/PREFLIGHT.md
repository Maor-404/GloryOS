# GloryOS Preflight & Upstream Research Report

**Milestone:** M0 — Architecture and Repository Initialization  
**Date:** 2026-11-26  
**Target Architecture:** `x86_64` (`amd64`)

---

## 1. Development Environment & Resource Inspection

All GloryOS development runs inside isolated workspaces, containers, and virtual machines so host operating systems are never mutated.

### Measured Workspace Resources

| Resource | Measured Value | Engineering Assessment & Build Constraints |
| :--- | :--- | :--- |
| **Workspace OS** | Ubuntu 24.04.5 LTS (`noble`), Kernel `6.18.57` (`x86_64`) | Debian/Ubuntu native packaging (`dpkg-deb`, `apt`) compatible |
| **CPU** | 2x Intel Xeon vCPUs @ 2.30 GHz (`x86_64`, AVX2) | Bound SquashFS/compile concurrency (`-processors 2`) to prevent OOM/thrashing |
| **Hardware KVM** | `/dev/kvm` **absent** (nested cloud VM) | QEMU tests **must** support `-accel kvm:tcg` (`tcg,thread=multi` fallback); keep M1 validation images lean with headless `ttyS0` serial probes |
| **Memory** | 7.8 GiB RAM (7.3 GiB free) + 8.0 GiB Swap | Sufficient for `mmdebstrap`, `mksquashfs`, and 2–3 GiB RAM QEMU UEFI guests |
| **Storage** | 98 GB `/` overlay (**85 GB free**, 9% used) | Sufficient for modular rootfs staging (`work/`) and ISO/QCOW2 artifacts (`out/`), provided build artifacts are cleaned between runs |
| **Isolation Primitives** | `unshare`, `/dev/loop0..7`, `/dev/fuse`, Docker `29.10.0` | Supports rootless/chroot `mmdebstrap`, `bubblewrap`, and containerized builds |

### Installed vs. Provisioned Development Toolchains

- **Preinstalled in base workspace:**
  - Languages & Runtimes: Python `3.12.16` (`uv 0.13.9`, `pytest 9.2`, `ruff 0.17`, `mypy 2.4`), Rust `1.100.0`, GCC/G++ `13.3.0`, Clang `18.1.3`, Go `1.24.3`, Node.js `22.23.5`, Microsoft **.NET SDK `10.0.115` & `8.0.134`**.
  - Utilities: `git 2.56`, `gh 2.103`, `cmake 3.28`, `ninja 1.11`, `make 4.3`, `dpkg-deb 1.22.6`, GNU `binutils 2.42` (`objdump`, `readelf`), `file`, `jq`, `rg`.
- **Provisioned by `scripts/setup-dev-env.sh` (~45.8 MB compressed download):**
  - Image & UEFI assembly: `mmdebstrap`, `debootstrap`, `squashfs-tools`, `xorriso`, `mtools`, `dosfstools`, `grub-efi-amd64-bin`, `grub-pc-bin`, `zstd`.
  - VM & UEFI testing: `qemu-system-x86`, `qemu-utils`, `ovmf` (EDK2 UEFI firmware).
  - Packaging, isolation & static analysis: `debhelper`, `fakeroot`, `lintian`, `shellcheck`, `bubblewrap`.
  - Project `.venv` Python packages: `pyyaml`, `jsonschema`, `pefile`, `pip-audit`, `pytest`, `ruff`, `mypy`.

> **Resource Policy:** Multi-gigabyte target dependencies (KDE Plasma desktop packages, Wine/Proton runtime tarballs, full Ubuntu live filesystems) are **never** installed onto the development host environment; they are fetched only inside isolated `M1+` rootfs/VM build stages with explicit milestone scope.

---

## 2. Upstream Technology Research & Maintenance Audit (Nov 2026)

| Domain | Selected Upstream | Maintenance Status (Nov 2026) | Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Base Distribution** | **Ubuntu 26.04 LTS (`resolute`)** *(with `24.04 noble` fallback)* | Active LTS (released April 2026, standard support until April 2031; mirrored on `archive.ubuntu.com`) | Ships Linux kernel 7.0 (`ntsync` module included), KDE Plasma 6.6 LTS, Qt 6.10, and .NET 8/10 in official Ubuntu repositories without unstable PPAs. |
| **Kernel** | Ubuntu LTS Linux Kernel (`linux-image-generic`) | Active upstream + Canonical security maintenance | Provides `/dev/ntsync` Windows NT sync driver (Linux 6.14+) when enabled via `/etc/modules-load.d/gloryos-ntsync.conf`. Zero custom kernel fork required. |
| **Desktop & Compositor** | **KDE Plasma 6.6 LTS + KWin (Wayland + XWayland)** | Active LTS upstream (KDE e.V. & Kubuntu team) | Native Wayland session by default, mature XWayland bridge for legacy X11/Wine apps, fractional scaling, tearing/VRR protocol support, and clean QML/Kirigami extensibility. |
| **System Installer** | **Calamares** *(evaluated against Ubuntu Subiquity)* | Active (`calamares` 3.3+/3.4 in Ubuntu `universe`, official installer of Kubuntu 24.04 & 26.04 LTS) | **Evaluation Result:** Ubuntu Desktop's `ubuntu-desktop-bootstrap` + `Subiquity` is packaged as a Canonical-branded Snap requiring `snapd` seed plumbing. **Calamares** is pure C++/Qt6 (`GPL-3.0-or-later`), installs from native `.deb` packages, supports UEFI + LUKS + ext4/Btrfs, requires zero online accounts or Snap infrastructure, and integrates natively with Plasma 6. |
| **Image Pipeline** | **`mmdebstrap` + `mksquashfs` + `grub-efi` + `xorriso`** | Active Debian/Ubuntu core tooling | Fully scriptable, deterministic CLI pipeline (unlike GUI-only `Cubic` or Snap-centric `ubuntu-image`). |
| **Windows Compatibility** | **WineHQ (`wine` 10.x Ubuntu / WineHQ 11.x)** | Active (`Wine 11.0+` released Jan 2026) | Wine 11 completes the **new WoW64 mode** (running 32-bit Windows PE binaries inside 64-bit Unix processes), improves `winewayland.drv`, and automatically uses `/dev/ntsync` when available. |
| **Standalone Proton** | **Valve Proton + `Open-Wine-Components/umu-launcher`** | Active collaborative upstream (Lutris, Heroic, Bottles, Open Wine Components) | Proton expects Steam's `SteamLinuxRuntime_sniper` container and `STEAM_COMPAT_*` env vars. `umu-launcher` (`umu-run`) executes Proton inside the open-source `sniper` runtime container **completely independently of the Steam client or Steam accounts**. |
| **Native .NET** | **Microsoft .NET 8 LTS & .NET 10 LTS** | Active (MIT, packaged in Ubuntu `main`) | Runs portable cross-platform CIL assemblies (`Console`, `ASP.NET`, `Avalonia`) natively on Linux without Wine overhead. |
| **WinGet Ecosystem** | **`microsoft/winget-pkgs` YAML Manifests** | Active community repository (schema `1.6.0`–`1.12.0`, MIT) | `winget-cli` itself depends on Windows APIs (MSI/MSIX/Registry/COM), so GloryOS consumes `winget-pkgs` declarative YAML manifests via a safe, read-only plan adapter rather than running Windows `winget.exe`. |

---

## 3. Licensing & Integration Constraints

1. **Ubuntu Derivative / Remix Policy:**
   - GloryOS cannot use Canonical's "Ubuntu" name or logo to imply official endorsement. Rebuilt/customized desktop Branding (`os-release`, Plymouth, SDDM, Calamares, Plasma Look-and-Feel) must carry GloryOS identity while accurately crediting Ubuntu LTS as the upstream base.
2. **Copyleft Compatibility (`GPL-3.0-or-later`, `LGPL-2.1-or-later`, `GPL-2.0-only`):**
   - KDE Plasma Workspace, Calamares, and `umu-launcher` are GPL-licensed. Licensing original GloryOS tools under **`GPL-3.0-or-later`** ensures clean compatibility across Qt6/KF6 (`LGPL-3.0` / `GPL-3.0`) and CLI tooling.
   - Wine (`LGPL-2.1+`), `umu-run` (`GPL-3.0`), `winetricks` (`LGPL-2.1+`), and `dotnet` (`MIT`) are invoked as distinct user-space processes over documented CLI/environment interfaces.
3. **Redistribution & Source Availability:**
   - Every generated GloryOS ISO/VM image **must** emit an inventory of exact `.deb` package versions (`manifest.packages`), preserve `/usr/share/doc/*/copyright`, and document `apt source` / upstream source archives for GPL/LGPL components (`Proton`, `Wine`, `Linux`, `GRUB`, `KDE`).
4. **Strict Non-Bundle Rule for Proprietary Software:**
   - Never bundle the proprietary Steam client, proprietary Microsoft Windows DLLs (`vcrun`, `mfc42`, Windows `.NET Desktop Runtime`), or proprietary fonts inside the base GloryOS ISO. User-authorized runtime prerequisites are fetched transparently on demand with checksum verification and license display.

---

## 4. Known Technical & Compatibility Limitations

GloryOS **never promises universal Windows compatibility**. GloryBridge and the WinGet adapter must detect these boundaries up front and fail gracefully with actionable diagnostics:

| Category | Hard Technical Limitation | GloryOS Detection & Mitigation Behavior |
| :--- | :--- | :--- |
| **Kernel-Mode Anti-Cheat & Drivers** | Windows kernel drivers (`.sys` — e.g., Vanguard, Ricochet, kernel-enforced EAC/BattlEye without Linux opt-in, USB/dongle drivers) cannot load into the Linux kernel. | Inspect PE imports (`ntoskrnl.exe`, `fltmgr.sys`, `wdm`) and known anti-cheat service descriptors; block launch with a clear diagnostic report before mutating prefixes. |
| **UWP / MSIX / Store Apps** | Encrypted Microsoft Store packages, `AppContainer` sandboxes, and `Windows.ApplicationModel.Store` APIs lack working Wine equivalents. | Reject `InstallerType: msix` / `appx` / `msstore` in WinGet plans with an explanation and native Linux alternative lookup. |
| **Windows-Only .NET UI Frameworks** | `.NET Framework 4.x`, **WPF** (`PresentationFramework`), **WinForms** (`System.Windows.Forms`), and **WinUI 3** (`Microsoft.UI.Xaml`) cannot run on Linux's native `dotnet` runtime. | Inspect CLR `AssemblyRef` and P/Invoke `ModuleRef` metadata; route portable CIL apps to native Linux `dotnet`, and route WPF/WinForms/`net4x` apps to an isolated Wine prefix with Wine-Mono or user-approved Windows .NET Desktop Runtime. |
| **Wayland vs. XWayland Quirks** | Legacy Win32 apps using global hotkeys, raw cursor warping, or child-window DirectX overlays may misbehave under pure `winewayland.drv`. | Support per-application display backend selection (`xwayland` default for maximum compatibility; opt-in `wayland` native driver in compatibility profiles). |
| **32-bit OpenGL & 16-bit Legacy** | Wine 11's new WoW64 mode has lower performance on legacy 32-bit OpenGL apps without 32-bit GL/Vulkan libraries, and 16-bit Win16/DOS executables are unsupported in pure 64-bit prefixes. | Detect PE magic (`PE32` vs `PE32+` vs `MZ`/`NE`); warn on 16-bit binaries and enable Vulkan/Zink/DXVK translation profiles where appropriate. |
| **GloryRebuild Boundaries** | Closed-source Windows executables cannot be recompiled; open-source apps tightly coupled to Win32, MFC, COM/ATL, or DirectX cannot be automatically compiled for Linux. | Restrict `GloryRebuild` strictly to verified open-source repositories; classify Win32/DirectX/MFC API usage in an honest feasibility report rather than attempting destructive source rewrites. |
