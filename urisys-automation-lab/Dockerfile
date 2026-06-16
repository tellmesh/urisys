FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/lab/packages/python \
    URISYS_LAB_HOST=0.0.0.0 \
    URISYS_LAB_PORT=8099 \
    URISYS_LAB_PACKS=stt,chat,webrtc \
    URISYS_LAB_FORWARD_SCHEMES=rdp,kvm,him,ocr,llm,browser,shell,http,https,env \
    URISYS_RDP_URL=http://urirdp:8795

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir PyYAML

WORKDIR /opt/lab

COPY urisys-automation-lab/packages/python ./packages/python
COPY urisys-automation-lab/server ./server
COPY urisys-automation-lab/web ./web
COPY urisys-automation-lab/flows ./flows
COPY urisys-automation-lab/docker/entrypoint.sh /usr/local/bin/lab-entrypoint

RUN chmod +x /usr/local/bin/lab-entrypoint \
    && mkdir -p /opt/lab/data

EXPOSE 8099

HEALTHCHECK --interval=10s --timeout=5s --retries=6 \
    CMD curl -fsS "http://127.0.0.1:${URISYS_LAB_PORT}/health" || exit 1

ENTRYPOINT ["/usr/local/bin/lab-entrypoint"]
CMD ["python3", "server/automation_lab_server.py"]
