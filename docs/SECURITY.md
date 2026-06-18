# Bezpieczeństwo Markpact / UriProcess

> Profil: [`MARKPACT-PROFILE.md`](MARKPACT-PROFILE.md) · architektura: [`PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md)

## Zasady ogólne

1. **Markpact z kodem Python (`markpact:handler`) = kod wykonywalny** — ładuj tylko z zaufanych źródeł (repo, podpisany wheel, materialized cache po review).
2. **Proces UriProcess bez handlerów użytkownika** — kroki to abstrakcyjne URI; implementacja w packach + resolverze.
3. **Mutacje** — `side_effects: true` + `approval: required` (minimum); produkcja: blok `risk`.
4. **Produkcja** — preferuj skompilowany/materialized artefakt (`.markpact/`) zamiast parsowania Markdown w runtime.

## Klasy ryzyka (`risk`)

| Klasa | Przykłady | Wymagania |
|-------|-----------|-----------|
| `read_observation` | `screen.frame`, `stepper.status` | audit opcjonalny |
| `physical_motion` | `stepper.move_relative` | approval, dry_run, limits, audit |
| `host_shell` | `shell.run` | approval, allowlist, timeout, cwd/env policy |
| `remote_session_mutation` | `rdp.session.prepare_target` | approval, audit |
| `capture_sensitive` | `screen.capture`, browser screenshot | approval, retention policy |
| `user_visible_output` | `tts.session.speak` | approval w produkcji |

Deklaracja w Markpact (v1alpha):

```yaml
risk:
  class: host_shell
  level: critical
  requires:
    - approval
    - command_allowlist
    - timeout
    - audit
```

## Shell (`shell://`)

Domyślny kontrakt: `command`, `side_effects: true`, `approval: required`.

**Produkcja** — profil resolvera / runtime config:

```yaml
policy:
  shell:
    allowlist:
      - apt-get
      - echo
    deny:
      - rm
      - curl
      - nc
      - ssh
    timeout_ms: 10000
    cwd_policy: fixed
    env_policy: minimal
```

`urisys markpact analyze --strict` ostrzega, gdy flow procesu używa `shell` bez zadeklarowanego `requires.schemes`.

## Stepper / hardware

Limity w resolverze (egzekwowane przed handlerem):

```yaml
policy:
  operations:
    stepper.move_relative:
      max: { steps: 10000, speed_sps: 1200 }
```

Profil urządzenia w `runtime.device_profile` + `require_dry_run_in_ci` (plan).

## Sandbox (plan v1beta)

```yaml
security:
  sandbox_required_for:
    - markpact://self/python/*
    - shell://*
  allow_auto_install: false
  allow_network: false
  allow_filesystem_write: false
```

## Context envelope (audit)

Minimum produkcyjne:

```yaml
context:
  approved: true
  dry_run: false
  environment: production
  trace_id: "..."
  actor: "operator@host"
  policy_profile: production
  audit:
    reason: "maintenance"
    ticket: "INC-123"
```

## CI / analyze

```bash
# procesy UriProcess — warnings = fail
urisys markpact analyze markpact-contracts/packs/machine-cycle-process.markpact.md --strict

bash urisys/scripts/analyze-process-markpacts.sh
```

Reguły ERROR (v1alpha): patrz [`MARKPACT-PROFILE.md`](MARKPACT-PROFILE.md).

## Dystrybucja

- Wheels z GitHub Releases — weryfikuj hash / tag.
- `urisys init` — tylko publiczne URLe wheeli (bez `git+https` na slave).
- Legacy `urisysedge` usunięty — edge runtime: `uricore` → `uri_control.edge`.
