# urirdp-docker OCI image
#
# Build from tellmesh workspace root:
#   docker build -f urisys/urirdp-docker/Dockerfile /home/tom/github/tellmesh
#
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

WORKDIR /build
COPY urisysedge /build/urisysedge
COPY urioperators /build/urioperators
COPY urirdp /build/urirdp
COPY urienv /build/urienv
COPY uribrowser /build/uribrowser
COPY urisys/urirdp-docker /build/urirdp-docker
COPY urisys/urirdp-docker/config /opt/urirdp/config
COPY urisys/urirdp-docker/flows /opt/urirdp/flows
COPY urisys/urirdp-docker/docker/startwm.sh /etc/xrdp/startwm.sh
COPY urisys/urirdp-docker/docker/bootstrap-rdp-session.sh /opt/urirdp/docker/bootstrap-rdp-session.sh
COPY urisys/urirdp-docker/docker/supervisord.conf /etc/supervisor/conf.d/urirdp.conf
COPY urisys/urirdp-docker/docker/entrypoint.sh /usr/local/bin/urirdp-entrypoint
RUN chmod +x /etc/xrdp/startwm.sh /opt/urirdp/docker/bootstrap-rdp-session.sh /usr/local/bin/urirdp-entrypoint \
    && python3 -m pip install --break-system-packages \
       -e /build/urisysedge \
       -e /build/urioperators \
       -e /build/urirdp \
       -e /build/urienv \
       -e /build/uribrowser \
       -e /build/urirdp-docker

WORKDIR /opt/urirdp
EXPOSE 3389 8795
ENTRYPOINT ["/usr/local/bin/urirdp-entrypoint"]
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/urirdp.conf"]
