#!/usr/bin/env python3
"""Simulate low-risk office activity via urisys node (HIM + optional LLM plan).

Examples:
  # Dry-run against local node (no real input):
  python3 scripts/office-simulate-loop.py --once --dry-run

  # One real tick (rules mode, no LLM):
  URISYS_ALLOW_REAL=1 python3 scripts/office-simulate-loop.py --once --mode rules

  # Loop every 60s with LLM plan per sub-step (needs OPENROUTER_API_KEY or mock phrase-map):
  URISYS_ALLOW_REAL=1 python3 scripts/office-simulate-loop.py --mode llm --interval 60
"""
from __future__ import annotations

import argparse
import json
import os
import random
import string
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8790"

LLM_STEPS = (
    "Office simulation: move mouse by 5-40 pixels to x={x} y={y}. Use him:// mouse move only, no click.",
    "Office simulation: type exactly one lowercase letter '{letter}'. Use him:// keyboard type only.",
    "Office simulation: scroll down slightly (amount -3). Use him:// mouse scroll only.",
)


def call_uri(base: str, uri: str, payload: dict | None, context: dict) -> dict:
    body = json.dumps({"uri": uri, "payload": payload or {}, "context": context}).encode("utf-8")
    req = urllib.request.Request(
        f"{base.rstrip('/')}/uri/call",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "error": f"HTTP {exc.code}: {detail}"}
    except urllib.error.URLError as exc:
        return {"ok": False, "error": str(exc.reason)}


def rules_tick(base: str, ctx: dict, letter: str) -> list[dict]:
    x = random.randint(200, 1200)
    y = random.randint(200, 800)
    actions = [
        ("him://local/mouse/command/move", {"x": x, "y": y}),
        ("him://local/keyboard/command/type", {"text": letter}),
        ("him://local/mouse/command/scroll", {"amount": -random.randint(1, 5)}),
    ]
    results = []
    for uri, payload in actions:
        out = call_uri(base, uri, payload, ctx)
        results.append(out)
        print(f"  {uri}: ok={out.get('ok')}")
        if not out.get("ok"):
            break
    return results


def llm_tick(base: str, ctx: dict, letter: str) -> list[dict]:
    x = random.randint(200, 1200)
    y = random.randint(200, 800)
    results = []
    for template in LLM_STEPS:
        transcript = template.format(x=x, y=y, letter=letter)
        plan = call_uri(
            base,
            "llm://local/text/query/plan",
            {"transcript": transcript, "allowed_schemes": ["him"]},
            ctx,
        )
        results.append(plan)
        if not plan.get("ok"):
            print(f"  plan failed: {plan.get('error') or plan}")
            continue
        result = plan.get("result") or {}
        uri = result.get("uri")
        payload = result.get("payload") or {}
        model = result.get("model", "?")
        print(f"  plan ({model}): {uri} {payload}")
        exec_out = call_uri(base, uri, payload, ctx)
        results.append(exec_out)
        print(f"  execute: ok={exec_out.get('ok')}")
        if not exec_out.get("ok"):
            break
    return results


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Office activity simulation loop for urisys node")
    parser.add_argument(
        "--base",
        default=os.environ.get("URISYS_URI_BASE", DEFAULT_BASE),
        help=f"Node base URL (default: {DEFAULT_BASE})",
    )
    parser.add_argument("--interval", type=int, default=60, help="Seconds between ticks (default: 60)")
    parser.add_argument(
        "--mode",
        choices=("rules", "llm"),
        default="rules",
        help="rules=deterministic HIM; llm=llm://text/query/plan per sub-step",
    )
    parser.add_argument("--once", action="store_true", help="Run one tick and exit")
    parser.add_argument("--dry-run", action="store_true", help="Pass dry_run in context (no real input)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    ctx = {
        "approved": True,
        "allow_real": not args.dry_run,
        "dry_run": args.dry_run,
    }
    if not args.dry_run and os.environ.get("URISYS_ALLOW_REAL") != "1":
        print("warning: set URISYS_ALLOW_REAL=1 for real HIM input", file=sys.stderr)

    tick = 0
    while True:
        tick += 1
        letter = random.choice(string.ascii_lowercase)
        print(f"[tick {tick}] letter={letter!r} mode={args.mode} dry_run={args.dry_run}")
        if args.mode == "rules":
            results = rules_tick(args.base, ctx, letter)
        else:
            results = llm_tick(args.base, ctx, letter)
        ok = all(r.get("ok") for r in results if r)
        print(f"[tick {tick}] done ok={ok}")
        if args.once:
            return 0 if ok else 1
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
