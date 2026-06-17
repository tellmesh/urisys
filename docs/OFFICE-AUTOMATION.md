# Automatyzacja biurowa — roadmap urisys

Pipeline sterowania maszyną przez URI: capture → analiza → akcja → weryfikacja.

Powiązane: [`FLOWS.md`](FLOWS.md), [`urisys-automation-lab/docs/10_AUTOMATIONS.md`](../urisys-automation-lab/docs/10_AUTOMATIONS.md), [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md).

## Pipeline docelowy

```text
screen:// / kvm:// capture  →  vql:// verify UI  →  imgl:// layout  →  him:// / browser://
                              ocr:// text          llm:// plan step
```

## Stan testów Docker (2026-06-17)

| Sesja | Wynik | Zrzuty |
|-------|-------|--------|
| `urisys-node-docker-gui` | **PASS** | `screen://` Xvfb, 8.8 KB PNG |
| `lab-10-flows` | **12/12 PASS** | 11 PNG RDP (fix flow 04 → example.com) |
| `urirdp-real-docker` | **PASS** | screenshot + OCR + xdotool click |
| `automation-lab` | **PASS** | chat → real KVM click |
| `remote-node-smoke` :8790 | **7/7** | identity, screen, hot-load kvm |
| `pytest-urisys-node` | **PASS** | 39 unit tests |
| `urirdp-rdp-e2e` | **PASS** | pipeline screenshot/ocr/llm/him + xdotool |
| `pytest-urirdp` | **18/19** | fail: `test_env_health_call` (env pack mock) |

Uruchomienie:

```bash
cd urisys
bash scripts/run-urisys-node-docker-e2e.sh          # screen:// :8790
python3 scripts/run_test_sessions.py --sessions lab-10-flows
python3 scripts/run_test_sessions.py --sessions urirdp-real-docker
```

Stack lab: `urisys-automation-lab/docker-compose.lab.yml` — porty **8099**, **8795**, **3389**.

## Przeglądarka (`browser://`)

- [x] Flow 03 — Chromium w RDP + zrzut
- [x] Flow 04 — download (kroki OK; doprecyzować `expect` zrzutu)
- [ ] SSO (Google/Microsoft) — profil persistent / CDP
- [ ] LinkedIn — post, komentarz, InMail (`vql://` verify modal)
- [ ] Formularze web — Typeform, Google Forms
- [x] Forward `browser://` na slave node → `uribrowser-docker` :8792 (`node-profile.lenovo.json`)
- [x] `browser://…/form/command/submit` (mock + policy approval)
- [ ] CDP bridge: Chrome na hoście bez RDP

## Office (`urioffice://` — pack vendored w `urikvm-docker`)

- [x] Schemat URI: open, save, export PDF (`urioffice://`)
- [x] Writer — tekst z `llm://` → TXT/DOCX + export PDF (mock/LibreOffice)
- [ ] Calc — CSV/env → arkusz → XLSX
- [ ] Impress — slajdy z planu `llm://`
- [ ] OnlyOffice Document Server (Docker) + forward pack
- [ ] MS365 web (Word/Excel online) przez `browser://`

## Email (`urimail://`)

- [x] Pack IMAP/SMTP — read (unread), compose, send (mock + Mailpit/SMTP gdy `URISYS_ALLOW_REAL=1`)
- [x] Dev mock: Mailpit (`urimail-docker/docker-compose.yml` — :8025/:1025)
- [x] Flow: nieprzeczytane → podsumowanie `llm://` → draft → send (`flows/email-mailpit.uri.flow.yaml`)
- [ ] Załącznik z dysku / zrzutu ekranu
- [ ] Outlook/Proton web przez browser automation

## Kalendarz i komunikacja

- [ ] Google Calendar — utwórz spotkanie
- [ ] Slack / Teams web — wiadomość na kanał
- [ ] Jira / Linear — ticket z `stt://` → `llm://` → browser

## Pliki i system

- [ ] Menedżer plików (Thunar) — upload, rename, zip
- [ ] PDF — merge, split, podpis (`shell://` + `ocr://`)
- [ ] `env://` + `shell://rclone` — sync folderów

## Weryfikacja i CI

- [x] `vql://` mock detect/compare (`urivql` pack, forward na slave opcjonalnie)
- [ ] `imgl://` — targets z layoutu zamiast sztywnych współrzędnych
- [x] Policy: approval na send-mail, submit-form, publish-post, export-pdf (`node-profile.*.json`)
- [ ] CI: `lab-10-flows` + `urisys-node-docker-gui` na merge
- [x] Sesje: `office-writer`, `email-mailpit` (+ istniejące `office-simulate`)

## Naprawione w trakcie testów (2026-06-17)

- `urirdp_shell` — shim do `urishell` łamał obraz Docker (`ModuleNotFoundError`); przywrócony lokalny handler subprocess.

## Symulacja pracy biurowej (lokalnie)

Jeden tick (move + litera + scroll) bez pętli:

```bash
cd urisys
export URISYS_ALLOW_REAL=1
urisys node serve --host 127.0.0.1 --port 8790   # osobny terminal

# dry-run (bez ruszania myszy):
urisys flow flows/office-simulate-tick.uri.flow.yaml --approve --dry-run

# real:
urisys flow flows/office-simulate-tick.uri.flow.yaml --approve --allow-real
```

Pętla co 60 s przez node HTTP (`rules` = deterministyczne HIM, `llm` = `llm://text/query/plan` na każdy sub-krok):

```bash
export URISYS_ALLOW_REAL=1
export URISYS_URI_BASE=http://127.0.0.1:8790
python3 scripts/office-simulate-loop.py --once --dry-run
python3 scripts/office-simulate-loop.py --mode llm --interval 60   # phrase-map bez API key
```

Packi: `him://…/mouse/command/scroll` (pyautogui / xdotool / ydotool→Page Down), `llm://…/text/query/plan` (phrase-map + opcjonalnie OpenRouter/OpenAI).

Test E2E (Docker Xvfb):

```bash
bash scripts/run-office-simulate-e2e.sh
python3 scripts/run_test_sessions.py --sessions office-simulate
```

W Dockerze HIM używa **xdotool** (Xvfb); na Wayland — **ydotool**; na pulpicie X11 — xdotool jeśli dostępny, inaczej pyautogui.

### Office writer + email (MVP packi)

Packi vendored (jak `urikvm`): `urioffice`, `urimail`, `urivql` w `urikvm-docker/packages/python/`.

```bash
# Writer: llm plan → render → export PDF
urisys flow flows/office-writer.uri.flow.yaml --approve --dry-run

# Email: unread → llm summary → compose → send
urisys flow flows/email-mailpit.uri.flow.yaml --approve --dry-run

# Browser + vql verify (forward browser:// na slave :8792)
urisys flow flows/browser-form-vql.uri.flow.yaml --approve --dry-run

# E2E Docker
bash scripts/run-office-writer-e2e.sh
bash scripts/run-email-mailpit-e2e.sh
python3 scripts/run_test_sessions.py --sessions office-writer,email-mailpit

# Mailpit lokalnie (opcjonalnie real SMTP z kontenera node)
docker compose -f urimail-docker/docker-compose.yml up -d
URISYS_MAILPIT=1 bash scripts/run-email-mailpit-e2e.sh
```

Na **lenovo** profil `urisys-node/config/node-profile.lenovo.json` forwarduje `browser://` → `:8792` i trzyma policy approval dla mail/form/post.

### Lenovo (192.168.188.201:8790)

```bash
# na lenovo (jednorazowo, gdy node nie działa):
systemctl --user enable --now urisys-node.service
# lub: ~/venv/bin/urisys-node serve --host 0.0.0.0 --port 8790

# z dev (212) — upgrade packi + test:
bash scripts/deploy-lenovo-node.sh
bash scripts/run-office-simulate-lenovo.sh              # dry-run
OFFICE_LENOVO_REAL=1 bash scripts/run-office-simulate-lenovo.sh   # real HIM

python3 scripts/run_test_sessions.py --sessions office-simulate-lenovo
```

Wheels serwowane z dev: `http://192.168.188.212:8765/` (`urihim-0.1.5`, `urillm-0.1.1`).
