#!/usr/bin/env python3
"""List browser profiles with active login sessions (cookie-based, read-only).

Usage:
  python3 scripts/scan-browser-sessions.py
  python3 scripts/scan-browser-sessions.py --linkedin-only
"""
from __future__ import annotations

import argparse
import configparser
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SESSION_CHECKS: dict[str, list[str]] = {
    "linkedin.com": ["li_at", "liap"],
    "github.com": ["user_session", "logged_in"],
    "google.com": ["SID", "SSID", "APISID"],
    "accounts.google.com": ["SID", "LSID"],
    "facebook.com": ["c_user", "xs"],
    "x.com": ["auth_token"],
    "twitter.com": ["auth_token"],
    "microsoft.com": ["ESTSAUTH", "ESTSAUTHPERSISTENT"],
    "reddit.com": ["reddit_session", "token_v2"],
    "stackoverflow.com": ["acct", "prov"],
    "gitlab.com": ["_gitlab_session"],
    "notion.so": ["token_v2"],
}


def _copy_query(db_path: Path, sql_chrome: str, sql_firefox: str) -> list[tuple]:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    try:
        shutil.copy2(db_path, tmp.name)
        con = sqlite3.connect(f"file:{tmp.name}?mode=ro", uri=True)
        cur = con.cursor()
        try:
            cur.execute(sql_chrome)
            kind = "chrome"
        except sqlite3.OperationalError:
            cur.execute(sql_firefox)
            kind = "firefox"
        rows = cur.fetchall()
        con.close()
        return kind, rows
    finally:
        os.unlink(tmp.name)


def scan_chrome_cookies(db_path: Path) -> dict[str, dict]:
    kind, rows = _copy_query(
        db_path,
        "SELECT host_key, name, expires_utc FROM cookies",
        "SELECT host, name, expiry FROM moz_cookies",
    )
    hits: dict[str, dict] = {}
    now_ff = int(datetime.now(timezone.utc).timestamp())
    for row in rows:
        host, name, exp = row[0], row[1], row[2]
        host = str(host).lstrip(".")
        for domain, names in SESSION_CHECKS.items():
            if host == domain or host.endswith("." + domain):
                if name not in names:
                    continue
                active = (kind == "firefox" and (exp == 0 or exp > now_ff)) or (
                    kind == "chrome" and (exp == 0 or exp > 13000000000000000)
                )
                slot = hits.setdefault(domain, {"cookies": set(), "logged_in": False})
                slot["cookies"].add(name)
                if active:
                    slot["logged_in"] = True
    return {d: {"cookies": sorted(v["cookies"]), "logged_in": v["logged_in"]} for d, v in hits.items()}


def chrome_profiles(base: Path) -> list[tuple[str, str, Path]]:
    out: list[tuple[str, str, Path]] = []
    names = {"Default": "Default"}
    local_state = base / "Local State"
    if local_state.exists():
        try:
            import json as _json

            data = _json.loads(local_state.read_text())
            for key, val in (data.get("profile", {}).get("info_cache") or {}).items():
                names[key] = val.get("name") or key
        except Exception:
            pass
    for prof in sorted(base.iterdir()):
        if not prof.is_dir():
            continue
        cookies = prof / "Cookies"
        network = prof / "Network" / "Cookies"
        path = cookies if cookies.exists() else network if network.exists() else None
        if path:
            out.append((prof.name, names.get(prof.name, prof.name), path))
    return out


def firefox_profiles(base: Path) -> list[tuple[str, str, Path]]:
    out: list[tuple[str, str, Path]] = []
    ini = base / "profiles.ini"
    if ini.exists():
        cp = configparser.RawConfigParser()
        cp.read(ini)
        for section in cp.sections():
            if not section.startswith("Profile"):
                continue
            rel = cp.get(section, "IsRelative", fallback="1") == "1"
            path = cp.get(section, "Path", fallback="")
            name = cp.get(section, "Name", fallback=section)
            prof = (base / path) if rel else Path(path)
            cookie = prof / "cookies.sqlite"
            if cookie.exists():
                out.append((prof.name, name, cookie))
    else:
        for prof in sorted(base.glob("*.default*")):
            cookie = prof / "cookies.sqlite"
            if cookie.exists():
                out.append((prof.name, prof.name, cookie))
    return out


def discover_browsers(home: Path) -> list[tuple[str, Path, str]]:
    return [
        ("google-chrome", home / ".config" / "google-chrome", "chrome"),
        ("chromium", home / ".config" / "chromium", "chrome"),
        ("brave", home / ".config" / "BraveSoftware" / "Brave-Browser", "chrome"),
        ("microsoft-edge", home / ".config" / "microsoft-edge", "chrome"),
        ("firefox", home / ".mozilla" / "firefox", "firefox"),
        ("firefox-snap", home / "snap" / "firefox" / "common" / ".mozilla" / "firefox", "firefox"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linkedin-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    home = Path.home()
    report: list[dict] = []
    for label, base, kind in discover_browsers(home):
        if not base.is_dir():
            continue
        profiles = firefox_profiles(base) if kind == "firefox" else chrome_profiles(base)
        for prof_id, prof_name, cookie_db in profiles:
            if "Guest" in prof_name:
                continue
            sessions = scan_chrome_cookies(cookie_db)
            if args.linkedin_only:
                sessions = {k: v for k, v in sessions.items() if "linkedin" in k}
            logged = [d for d, info in sessions.items() if info.get("logged_in")]
            if not sessions:
                continue
            report.append(
                {
                    "browser": label,
                    "profile_id": prof_id,
                    "profile_name": prof_name,
                    "cookie_db": str(cookie_db),
                    "logged_in_domains": logged,
                    "sessions": sessions,
                }
            )

    bins = {cmd: shutil.which(cmd) for cmd in ("firefox", "google-chrome", "chromium", "brave-browser", "microsoft-edge")}

    if args.json:
        print(json.dumps({"host": os.uname().nodename, "browsers": bins, "profiles": report}, indent=2))
        return 0

    print(f"Host: {os.uname().nodename}")
    print("Installed:", ", ".join(f"{k}={v}" for k, v in bins.items() if v) or "(none)")
    print()
    if not report:
        print("No login session cookies found.")
        return 0
    for item in report:
        status = "LOGGED IN" if item["logged_in_domains"] else "stale/anonymous only"
        print(f"{item['browser']} / {item['profile_name']} ({item['profile_id']}) — {status}")
        print(f"  {item['cookie_db']}")
        if item["logged_in_domains"]:
            print(f"  domains: {', '.join(item['logged_in_domains'])}")
        elif args.linkedin_only:
            li = item["sessions"].get("linkedin.com")
            if li:
                print(f"  linkedin cookies (no auth): {', '.join(li['cookies'])}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
