FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    RDP_USER=urisys \
    RDP_PASSWORD=urisys \
    RDP_PORT=3389 \
    URISYS_RDP_PORT=8795 \
    URISYS_KVM_DISPLAY=:10

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git sudo supervisor procps net-tools \
    python3 python3-pip python3-venv python3-setuptools \
    xrdp xorgxrdp xfce4 xfce4-terminal dbus-x11 \
    x11-apps xdotool scrot imagemagick tesseract-ocr x11-utils \
    freerdp2-x11 zenity xvfb \
    fonts-dejavu xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/urirdp
COPY pyproject.toml ./
COPY packages ./packages
COPY config ./config
COPY flows ./flows
COPY docker/startwm.sh /etc/xrdp/startwm.sh
COPY docker/bootstrap-rdp-session.sh /opt/urirdp/docker/bootstrap-rdp-session.sh
COPY docker/supervisord.conf /etc/supervisor/conf.d/urirdp.conf
COPY docker/entrypoint.sh /usr/local/bin/urirdp-entrypoint
RUN chmod +x /etc/xrdp/startwm.sh /opt/urirdp/docker/bootstrap-rdp-session.sh /usr/local/bin/urirdp-entrypoint \
    && python3 -m pip install --break-system-packages -e ".[real]"

EXPOSE 3389 8795
ENTRYPOINT ["/usr/local/bin/urirdp-entrypoint"]
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/urirdp.conf"]
