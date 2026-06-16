FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    RDP_USER=urisys \
    RDP_PASSWORD=urisys \
    RDP_PORT=3389 \
    URISYS_RDP_PORT=8795 \
    URISYS_KVM_DISPLAY=:10 \
    URISYS_ENV_POLICY=/opt/urirdp/config/env-policy.yaml

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git sudo supervisor procps net-tools \
    python3 python3-pip python3-venv python3-setuptools \
    xrdp xorgxrdp xfce4 xfce4-terminal dbus-x11 \
    x11-apps xdotool scrot imagemagick tesseract-ocr x11-utils \
    freerdp2-x11 zenity xvfb htop nano \
    fonts-dejavu xauth chromium \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/urirdp
COPY urirdp-docker/pyproject.toml ./
COPY packages/python/urisysedge ./packages/python/urisysedge
COPY urirdp-docker/packages ./packages
COPY urirdp-docker/config ./config
COPY urirdp-docker/flows ./flows
COPY urirdp-docker/docker/startwm.sh /etc/xrdp/startwm.sh
COPY urirdp-docker/docker/bootstrap-rdp-session.sh /opt/urirdp/docker/bootstrap-rdp-session.sh
COPY urirdp-docker/docker/supervisord.conf /etc/supervisor/conf.d/urirdp.conf
COPY urirdp-docker/docker/entrypoint.sh /usr/local/bin/urirdp-entrypoint
COPY urienv-docker/packages/python/urienv /tmp/vendor/urienv
COPY uribrowser-docker /tmp/vendor/uribrowser-docker
RUN chmod +x /etc/xrdp/startwm.sh /opt/urirdp/docker/bootstrap-rdp-session.sh /usr/local/bin/urirdp-entrypoint \
    && python3 -m pip install --break-system-packages "uricore>=0.1.2" \
    && python3 -m pip install --break-system-packages -e ".[real]" \
       -e /tmp/vendor/urienv \
       -e /tmp/vendor/uribrowser-docker

ENV PYTHONPATH="/opt/urirdp/packages/python"

EXPOSE 3389 8795
ENTRYPOINT ["/usr/local/bin/urirdp-entrypoint"]
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/urirdp.conf"]
