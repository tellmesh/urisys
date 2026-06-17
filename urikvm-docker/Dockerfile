# urikvm-docker OCI image (kvm/him/ocr/llm bundle)
#
# Build from tellmesh workspace root (sibling repos required):
#   docker build -f urisys/urikvm-docker/Dockerfile /home/tom/github/tellmesh
#
FROM python:3.12-slim
WORKDIR /build
COPY urisysedge /build/urisysedge
COPY urioperators /build/urioperators
COPY urikvm /build/urikvm
COPY urihim /build/urihim
COPY uriocr /build/uriocr
COPY urillm /build/urillm
COPY urisys/urikvm-docker /build/urikvm-docker
RUN pip install --no-cache-dir \
    -e /build/urisysedge \
    -e /build/urioperators \
    -e /build/urikvm \
    -e /build/urihim \
    -e /build/uriocr \
    -e /build/urillm \
    -e /build/urikvm-docker
WORKDIR /build/urikvm-docker
EXPOSE 8794
CMD ["urisys-kvm", "serve", "--host", "0.0.0.0", "--port", "8794"]
