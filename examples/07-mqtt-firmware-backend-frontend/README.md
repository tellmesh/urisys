# 07-mqtt-firmware-backend-frontend

End-to-end MQTT example: firmware simulator, MQTT broker, backend HTTP bridge,
and a frontend page that calls explicit URI commands mapped to MQTT topics.

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
- `uri_contract.py` and `frontend/uri-contract.js` - shared URI command/query constants and CQRS helpers.
- `firmware.py` - simulated firmware using raw MQTT over TCP.
- `backend.py` - `/api/uri/call` HTTP bridge; maps URI commands to MQTT topics.
- `frontend/` - browser UI calling `/api/uri/call` with URI constants.

Core URI constants:

```text
mqtt://device-01/led/command/set
mqtt://device-01/ping/command/send
mqtt://device-01/state/query/current
mqtt://device-01/telemetry/query/latest
```

Frontend CQRS usage:

```js
import { Command, Query } from './uri-contract.js';

await callUri(Command.setLed(true));
await callUri(Query.stateCurrent());
```

Default ports:

- MQTT broker: `127.0.0.1:18883`
- HTTP backend/frontend: `127.0.0.1:8097`

Override with `MQTT_PORT` and `HTTP_PORT`.
