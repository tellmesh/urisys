# 07-mqtt-firmware-backend-frontend

End-to-end MQTT example: firmware simulator, MQTT broker, backend HTTP bridge,
and a frontend page that calls backend endpoints mapped to MQTT topics.

```bash
bash examples/07-mqtt-firmware-backend-frontend/run.sh
```

Open:

```text
http://127.0.0.1:8097/
```

Smoke mode exits automatically:

```bash
bash examples/07-mqtt-firmware-backend-frontend/run.sh --smoke
```

Layers:

- `mqtt_codec.py` - tiny MQTT 3.1.1 broker/client for this example, QoS 0 only.
- `firmware.py` - simulated firmware using raw MQTT over TCP.
- `backend.py` - HTTP API and static frontend server; publishes/subscribes via MQTT.
- `frontend/` - browser UI calling `/api/...` endpoints.

Default ports:

- MQTT broker: `127.0.0.1:18883`
- HTTP backend/frontend: `127.0.0.1:8097`

Override with `MQTT_PORT` and `HTTP_PORT`.
