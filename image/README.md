# GloryOS Image & Installer Pipeline (`image/`)

**Owned Roles:** Build Engineer, Linux Engineer  
**Active Milestones:** M1 (Bootable Ubuntu UEFI Image), M9 (Calamares Offline Installer)

## Scope
- Declarative `mmdebstrap` rootfs assembly from [`configs/distro/gloryos-base.yaml`](../configs/distro/gloryos-base.yaml).
- Kernel module configuration (`/etc/modules-load.d/gloryos-ntsync.conf`) and udev rules.
- UEFI `BOOTX64.EFI` (`grub-mkstandalone`) + SquashFS + `xorriso` hybrid ISO generation.
- Calamares offline installer configuration (`M9`).
- Automated SBOM (`manifest.packages`) and `/usr/share/doc/*/copyright` extraction (`manifest.licenses`).
- Headless QEMU + OVMF (`-accel kvm:tcg`) serial boot verification scripts.

> **Host Safety Rule:** Image scripts must operate strictly inside `work/` and `out/` (or containers/VMs) and never modify the host `/etc` or `/boot`.
