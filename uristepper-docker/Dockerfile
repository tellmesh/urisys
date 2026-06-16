FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/packages/python \
    URISYS_DEVICE_PROFILE=/app/config/device-profile.json \
    URISYS_EVENTS_PATH=/data/events.jsonl \
    URISYS_STATE_PATH=/data/stepper_state.json \
    URISYS_NODE_ID=uristepper-docker

WORKDIR /app
COPY packages/python/urisysedge ./packages/python/urisysedge
COPY uristepper-docker/ .
RUN mkdir -p /data
EXPOSE 8790
CMD ["python", "-m", "uristepperedge", "serve", "--host", "0.0.0.0", "--port", "8790"]
