FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl jq git ca-certificates \
    && curl -fsSL "https://download.docker.com/linux/static/stable/$(uname -m)/docker-27.3.1.tgz" \
      | tar xz -C /usr/local/bin --strip-components=1 docker/docker \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

CMD ["bash"]
