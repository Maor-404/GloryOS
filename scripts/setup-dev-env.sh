#!/usr/bin/env bash
# Idempotent, non-interactive workspace setup for GloryOS development.
# - On isolated cloud devboxes / CI VMs: installs lightweight CLI build, QEMU/UEFI,
#   packaging, and static-analysis tools (~46 MB) if missing, plus an isolated .venv.
# - Set GLORYOS_SKIP_APT=1 on bare-metal developer workstations to skip APT installs
#   and only provision the repository-local Python virtual environment (.venv).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

APT_PACKAGES=(
  bubblewrap
  debhelper
  debootstrap
  dosfstools
  fakeroot
  grub-efi-amd64-bin
  grub-pc-bin
  lintian
  mmdebstrap
  mtools
  ovmf
  qemu-system-x86
  qemu-utils
  shellcheck
  squashfs-tools
  xorriso
  zstd
)

install_apt_tools_if_needed() {
  if [[ "${GLORYOS_SKIP_APT:-0}" == "1" ]]; then
    echo "[setup] GLORYOS_SKIP_APT=1 set; skipping system APT package check."
    return 0
  fi

  if ! command -v apt-get >/dev/null 2>&1 || ! command -v dpkg-query >/dev/null 2>&1; then
    echo "[setup] Non-APT host detected; skipping APT package step."
    return 0
  fi

  local missing=()
  local pkg
  for pkg in "${APT_PACKAGES[@]}"; do
    if ! dpkg-query -W -f='${Status}' "${pkg}" 2>/dev/null | grep -qx "install ok installed"; then
      missing+=("${pkg}")
    fi
  done

  if [[ "${#missing[@]}" -eq 0 ]]; then
    echo "[setup] All required APT workspace packages are already installed."
    return 0
  fi

  echo "[setup] Installing missing workspace packages: ${missing[*]}"
  local sudo_cmd=()
  if [[ "${EUID}" -ne 0 ]]; then
    sudo_cmd=(sudo)
  fi

  "${sudo_cmd[@]}" env DEBIAN_FRONTEND=noninteractive apt-get update -qq
  "${sudo_cmd[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
    "${missing[@]}"
}

provision_python_venv() {
  echo "[setup] Provisioning isolated Python environment at ${VENV_DIR}"
  if command -v uv >/dev/null 2>&1; then
    if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
      uv venv --python python3 "${VENV_DIR}"
    fi
    uv pip install --python "${VENV_DIR}/bin/python" --quiet -e "${REPO_ROOT}[dev]"
  else
    if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
      python3 -m venv "${VENV_DIR}"
    fi
    "${VENV_DIR}/bin/pip" install --quiet --upgrade "pip>=26.2"
    "${VENV_DIR}/bin/pip" install --quiet --disable-pip-version-check -e "${REPO_ROOT}[dev]"
  fi
}

persist_cloud_shell_path() {
  # Cloud agent shells source ~/.bashrc non-interactively via BASH_ENV.
  if [[ "${USER:-}" == "antigravity" && -f "${HOME}/.bashrc" ]]; then
    sed -i '/case \$- in/,/esac/d' "${HOME}/.bashrc" 2>/dev/null || true
    local export_line="export PATH=\"${VENV_DIR}/bin:\$PATH\""
    grep -qxF "${export_line}" "${HOME}/.bashrc" || echo "${export_line}" >> "${HOME}/.bashrc"
  fi
}

main() {
  install_apt_tools_if_needed
  provision_python_venv
  persist_cloud_shell_path
  "${VENV_DIR}/bin/gloryos" preflight --milestone M1
}

main "$@"
