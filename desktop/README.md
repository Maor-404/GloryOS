# GloryOS KDE Plasma 6 Integration (`desktop/`)

**Owned Roles:** Desktop Engineer  
**Active Milestones:** M2 (KDE Plasma Integration & Branding), M4 (Shortcuts & Control Center)

## Scope
- GloryOS Look-and-Feel package, SDDM theme configuration, wallpaper, and `/etc/os-release` branding (strictly respecting Ubuntu Remix trademark rules).
- Wayland-first KWin + XWayland session defaults.
- Dolphin file manager service menus for inspecting `.exe` / `.msi` files via `GloryBridge` (never auto-executing installers).
- `Glory Control Center` & `Glory Settings` (Qt 6 / Kirigami) consuming [`schemas/compatibility-profile.schema.json`](../schemas/compatibility-profile.schema.json) and [`schemas/executable-inspection.schema.json`](../schemas/executable-inspection.schema.json).
