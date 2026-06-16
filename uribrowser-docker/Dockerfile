FROM python:3.12-slim
WORKDIR /app
COPY packages/python/urisysedge ./packages/python/urisysedge
COPY uribrowser-docker/ .
ENV PYTHONPATH=/app/packages/python
RUN pip install --no-cache-dir -e .
EXPOSE 8792
CMD ["urisys-browser", "serve", "--host", "0.0.0.0", "--port", "8792"]
