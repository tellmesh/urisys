# browser:// portability

`browser://` is a contract, not a browser implementation.

The same URI can be routed to different drivers:

- `mock` — deterministic test driver, works everywhere.
- `system-open` — calls the OS default browser via Python `webbrowser`.
- `playwright` — real headless Chromium/Firefox/WebKit when dependencies are installed.
- `remote-cdp` — placeholder for a remote Chrome DevTools Protocol bridge.

Transport URL example:

```text
POST http://server:8792/uri/call
```

Logical command:

```text
browser://default/page/command/open
```

The app should keep using `browser://`; only routing/profile decides which driver/system handles it.
