# urisys examples

Katalog jest plaski: kazdy przyklad ma postac `NN-name/` i zawiera co najmniej
`README.md` oraz `run.sh`.

| Przyklad | Uruchomienie | Zakres |
|----------|--------------|--------|
| `01-call-uri` | `bash examples/01-call-uri/run.sh` | Pojedyncze URI przez CLI |
| `02-server-curl` | `bash examples/02-server-curl/run.sh` | HTTP `POST /uri/call` do dzialajacego `urisys serve` |
| `03-threaded-uri-runtime` | `bash examples/03-threaded-uri-runtime/run.sh` | Rownolegle URI call i procesy flow |
| `04-markpact-browser-call` | `bash examples/04-markpact-browser-call/run.sh` | Markpact jako runtime manifest bez instalowania packa |
| `05-markpact-showcase-run-flow` | `bash examples/05-markpact-showcase-run-flow/run.sh` | Embedded Markpact flows |
| `06-frontend` | `bash examples/06-frontend/run.sh` | Browser UI z `uricontrol-js` |
| `07-mqtt-firmware-backend-frontend` | `bash examples/07-mqtt-firmware-backend-frontend/run.sh` | Firmware + backend + frontend przez MQTT |
