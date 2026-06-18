# UriProcess conformance matrix

> Dry-run conformance for reference process Markpacts. CI: `tests/test_process_conformance.py`

## Reference processes

| Markpact | Flow | Resolver | Expect |
|----------|------|----------|--------|
| `machine-cycle-process` | `machine-cycle` | optional (Pololu example) | `transport_ok`, `required_steps` |
| `desktop-automation-processes` | `gui-open-software-center` | — | `ocr_contains` |
| `desktop-automation-processes` | `rdp-kvm-smoke` | — | `ocr_contains` |
| `desktop-automation-processes` | `install-update-verify-browser` | `urisys.runtime.resolver.yaml` | `opened_url_contains` |

## Runtime matrix (analyze + dry-run)

| Capability | analyze strict | dry-run flow | resolver |
|------------|----------------|--------------|----------|
| stepper | ✅ `uristepper` | ✅ machine-cycle | Pololu hybrid YAML |
| kvm/ocr/llm/him | ✅ matrix test | ✅ desktop flows | — |
| shell/screen/env | ✅ matrix test | — | `policy.shell.allowlist` |
| rdp/browser | ✅ matrix test | — | — |
| package:// | — | — | `uri_aliases` required |

CI:
- `tests/test_capability_conformance.py` — analyze matrix (10 thin packs)
- `tests/test_process_conformance.py` — dry-run process flows
- `tests/test_golden_analyze.py` — snapshot analyze reference processes

## Commands

```bash
export TELLMESH_ROOT=~/github/tellmesh
cd urisys
pytest tests/test_process_conformance.py -q
urisys markpact analyze markpact-contracts/packs/machine-cycle-process.markpact.md --strict
```

Powiązane: [`MARKPACT-PROFILE.md`](MARKPACT-PROFILE.md) · [`SECURITY.md`](SECURITY.md) · [`RESOLVER-SCHEMA.md`](RESOLVER-SCHEMA.md)
