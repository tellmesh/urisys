# 02-server-curl

Bezposredni HTTP call do dzialajacego serwera `urisys serve`.

W pierwszym terminalu:

```bash
urisys --packs llm serve --port 8789
```

W drugim terminalu:

```bash
bash examples/02-server-curl/run.sh
```

Domyslny endpoint to `http://127.0.0.1:8789`. Mozesz go zmienic przez
`URISYS_ENDPOINT`.
