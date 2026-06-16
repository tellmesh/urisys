FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY packages/python/urisysedge /app/packages/python/urisysedge
COPY packages/python/urienv /app/packages/python/urienv
COPY docker/config /app/docker/config
COPY flows /app/flows
COPY tests /app/tests

RUN pip install --upgrade pip \
    && pip install "PyYAML>=6.0" "uricore>=0.1.3" \
    && printf '%s\n' '#!/usr/bin/env sh' 'exec python -m urisysedge.cli "$@"' > /usr/local/bin/urisys \
    && chmod +x /usr/local/bin/urisys \
    && ln -s /usr/local/bin/urisys /usr/local/bin/urisys-edge

ENV PYTHONPATH="/app/packages/python/urisysedge/src:/app/packages/python/urienv/src"

EXPOSE 8790

HEALTHCHECK --interval=10s --timeout=3s --retries=10 CMD python - <<'PY'
import json, urllib.request
with urllib.request.urlopen('http://127.0.0.1:8790/health', timeout=2) as r:
    data=json.loads(r.read().decode())
    assert data.get('ok') is True
PY

CMD ["urisys", "serve", "--packs", "env", "--host", "0.0.0.0", "--port", "8790", "--env-config", "/etc/urisys/env-policy.yaml"]
