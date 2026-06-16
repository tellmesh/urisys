#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${RDP_USER:-urisys}"
USER_PASS="${RDP_PASSWORD:-urisys}"

if ! id "$USER_NAME" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$USER_NAME"
  usermod -aG sudo "$USER_NAME"
fi

echo "$USER_NAME:$USER_PASS" | chpasswd
echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${USER_NAME}-lab"
chmod 440 "/etc/sudoers.d/${USER_NAME}-lab"
mkdir -p /home/$USER_NAME/.config/xfce4 /opt/urirdp/data/screenshots
chown -R "$USER_NAME:$USER_NAME" /home/$USER_NAME /opt/urirdp/data || true

# XRDP needs this cert group in Debian-based images.
adduser xrdp ssl-cert >/dev/null 2>&1 || true

export URISYS_RDP_PORT="${URISYS_RDP_PORT:-8795}"
export URISYS_CONFIG="${URISYS_CONFIG:-/opt/urirdp/config/rdp-kvm-profile.json}"
export URISYS_ALLOW_REAL="${URISYS_ALLOW_REAL:-0}"

exec "$@"
