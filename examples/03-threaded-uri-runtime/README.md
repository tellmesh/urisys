# 03-threaded-uri-runtime

Samowystarczalny smoke test rownoleglosci `urisys`.

```bash
bash examples/03-threaded-uri-runtime/run.sh
```

Skrypt tworzy tymczasowy mock-pack, uruchamia lokalny HTTP runtime na wolnym
porcie, odpala rownolegle `/uri/call`, a potem uruchamia kilka procesow CLI
wykonujacych ten sam flow.
