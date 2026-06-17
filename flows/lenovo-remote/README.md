# lenovo-remote flows (moved)

Flow suites for the lenovo slave node live in **urisys-examples**:

```
../urisys-examples/lenovo-remote/
```

Run from **urisys**:

```bash
cd ../urisys
python3 scripts/lenovo_remote_session.py --build-wheels --wait 90
python3 scripts/lenovo_remote_session.py --wait 60 --flows lenovo-remote/08-kvm-linkedin.uri.flow.yaml
```

See [`urisys-examples/lenovo-remote/README.md`](../../urisys-examples/lenovo-remote/README.md).
