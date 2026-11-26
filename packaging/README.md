# GloryOS Packaging & Ecosystem Mapping (`packaging/`)

**Owned Roles:** Package Engineer, Security Auditor  
**Active Milestones:** M2–M8 (`.deb` packaging), M7 (APT & WinGet Plan Adapter)

## Scope
- Native Debian packaging (`debian/` metadata built via `debhelper` and audited with `lintian`) for original GloryOS packages (`gloryos-desktop-branding`, `glory-bridge`, `glory-pkg`, `glory-rebuild`).
- Curated native Linux package mapping table (`native-alternatives.yaml`) mapping popular WinGet `PackageIdentifier` entries to native Ubuntu APT packages before falling back to Windows compatibility environments.
