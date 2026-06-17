# uribrowser-docker OCI image
#
# Build from tellmesh workspace root:
#   docker build -f urisys/uribrowser-docker/Dockerfile /home/tom/github/tellmesh
#
FROM python:3.12-slim
WORKDIR /build
COPY urisysedge /build/urisysedge
COPY uribrowser /build/uribrowser
COPY urisys/uribrowser-docker /build/uribrowser-docker
RUN pip install --no-cache-dir \
    -e /build/urisysedge \
    -e /build/uribrowser \
    -e /build/uribrowser-docker
WORKDIR /build/uribrowser-docker
EXPOSE 8792
CMD ["urisys-browser", "serve", "--host", "0.0.0.0", "--port", "8792"]
