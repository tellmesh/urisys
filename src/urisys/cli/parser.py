from __future__ import annotations

import argparse
import os
from pathlib import Path

from ..defaults import (
    DEFAULT_ENVIRONMENT,
    DEFAULT_EVENTS_PATH,
    DEFAULT_MIN_VERSION,
    MIN_VERSION_ENV,
)


def add_runtime_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-real", action="store_true")
    parser.add_argument("--environment", default=DEFAULT_ENVIRONMENT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="urisys", description="URI control system: managers/controllers over uri* packs and UriPack Markpacts.")
    parser.add_argument("--packs", default="all", help="Comma-separated pack aliases/packages, plain manifest paths, Markpact paths or all/none.")
    parser.add_argument("--markpact", action="append", default=[], help="Load one UriPack Markpact. Can be used multiple times.")
    parser.add_argument("--events", default=DEFAULT_EVENTS_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("call", help="Execute a URI through urisys.")
    p.add_argument("uri")
    p.add_argument("--payload", default="{}", help="JSON payload or @file.json")
    add_runtime_flags(p)

    p = sub.add_parser("explain", help="Explain how a URI routes.")
    p.add_argument("uri")

    sub.add_parser("routes", help="List loaded routes.")
    sub.add_parser("events", help="List event log.")

    p = sub.add_parser("flow", help="Run a compact URI flow YAML.")
    p.add_argument("path")
    add_runtime_flags(p)

    p = sub.add_parser("doctor", help="Check installation, Python env, and dependencies.")
    p.add_argument(
        "--min-version",
        default=os.environ.get(MIN_VERSION_ENV, DEFAULT_MIN_VERSION),
        help=f"Minimum urisys version (default: {DEFAULT_MIN_VERSION}).",
    )

    p = sub.add_parser(
        "init",
        help="Install uricontrol/uriguard + urisys[real], doctor, write slave env (~/.config/urisys/node.env).",
    )
    p.add_argument("--profile", choices=("slave", "dev"), default=os.environ.get("URISYS_INIT_PROFILE", "slave"))
    p.add_argument("--min-version", default=os.environ.get(MIN_VERSION_ENV, DEFAULT_MIN_VERSION))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-pip", action="store_true")
    p.add_argument("--no-write-env", action="store_true")
    p.add_argument("--env-file", default=str(Path.home() / ".config" / "urisys" / "node.env"))

    p = sub.add_parser("serve", help="Run HTTP URI server (dev packs; for desktop slave use: urisys node serve).")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8789)

    node = sub.add_parser("node", help="urisys-node slave runtime (bundled; lazy pack install via URI).")
    node_sub = node.add_subparsers(dest="node_command", required=True)
    ns = node_sub.add_parser(
        "serve",
        help="Start node HTTP server (:8790); kills any prior listener on the port (atomic restart).",
    )
    ns.add_argument("--host", default=os.environ.get("URISYS_NODE_HOST", "0.0.0.0"))
    ns.add_argument("--port", type=int, default=int(os.environ.get("URISYS_NODE_PORT", "8790")))
    ns.add_argument("--config", default=os.environ.get("URISYS_NODE_CONFIG", "config/node-profile.json"))
    ns.add_argument(
        "--no-takeover",
        action="store_true",
        help="Do not kill an existing listener on --port.",
    )
    ns.add_argument(
        "--no-auto-install",
        action="store_true",
        help="Disable URISYS_NODE_AUTO_INSTALL (no pip on first kvm/him/… URI).",
    )

    nr = node_sub.add_parser(
        "remote",
        help="Remote node ops (alias for `urisys remote`; dev host → lenovo).",
    )
    nr.add_argument(
        "remote_argv",
        nargs=argparse.REMAINDER,
        help="e.g. health | restart | call URI",
    )

    rem = sub.add_parser(
        "remote",
        help="Remote node ops via URI (health, restart, call, workers; same as urisys-node remote).",
    )
    rem.add_argument(
        "remote_argv",
        nargs=argparse.REMAINDER,
        help="e.g. health | restart | call URI | upgrade-node",
    )

    p = sub.add_parser("markpact", help="Validate, compile, fetch and test one-file UriPack Markpacts.")
    msub = p.add_subparsers(dest="markpact_command", required=True)

    p_fetch = msub.add_parser("fetch", help="Fetch a Markpact from file/HTTP/GitHub/git/ZIP and cache it locally.")
    p_fetch.add_argument("source")
    p_fetch.add_argument("--force", action="store_true")

    p_validate = msub.add_parser("validate", help="Validate a Markpact file or remote source.")
    p_validate.add_argument("path")

    p_compile = msub.add_parser("compile", help="Compile Markpact to cached runtime manifest and handlers.")
    p_compile.add_argument("path")
    p_compile.add_argument("--out", default=None, help="Optional output/cache directory.")
    p_compile.add_argument("--force", action="store_true")

    p_routes = msub.add_parser("routes", help="Compile Markpact and list generated routes.")
    p_routes.add_argument("path")
    p_routes.add_argument("--out", default=None)

    p_test = msub.add_parser("test", help="Run tests embedded in Markpact.")
    p_test.add_argument("path")
    p_test.add_argument("--out", default=None, help="Optional compile/cache directory.")

    p_gen = msub.add_parser("gen-contract", help="Generate a UriContract Markpact from a runtime manifest.yaml.")
    p_gen.add_argument("manifest", help="Path to a pack manifest.yaml.")
    p_gen.add_argument("--out", default=None, help="Write contract to this file (default: print to stdout).")
    p_gen.add_argument("--stdout", action="store_true", help="Print to stdout (default when --out is omitted).")
    p_gen.add_argument("--force", action="store_true", help="Overwrite --out if it already exists.")

    p_drift = msub.add_parser("check-drift", help="Compare a manifest.yaml against an existing UriContract Markpact.")
    p_drift.add_argument("manifest", help="Path to a pack manifest.yaml.")
    p_drift.add_argument("contract", help="Path/source of the UriContract Markpact.")

    p_analyze = msub.add_parser("analyze", help="Summarise a showcase Markpact: definitions, embedded flows (use_case/integration), protos.")
    p_analyze.add_argument("path")
    p_analyze.add_argument(
        "--strict",
        action="store_true",
        help="Treat profile v1alpha warnings as errors (CI for UriProcess packs).",
    )
    p_analyze.add_argument(
        "--strict-operations",
        action="store_true",
        help="Treat non-namespaced operation warnings as errors.",
    )
    p_analyze.add_argument(
        "--json",
        action="store_true",
        help="Emit stable CI contract (MP + RR issue codes in one report).",
    )

    p_run_flow = msub.add_parser(
        "run-flow",
        help="Compile Markpact, build uri_control.edge runtime (manifest + uses: packs) and run an embedded flow.",
    )
    p_run_flow.add_argument(
        "path",
        help="Markpact path or markpact://… with optional #flow.id fragment (e.g. showcase.md#open-and-read).",
    )
    p_run_flow.add_argument("--out", default=None, help="Optional compile/cache directory.")
    p_run_flow.add_argument("--force", action="store_true", help="Force recompile before run.")
    p_run_flow.add_argument(
        "--extra-packs",
        default="",
        help="Additional pack aliases to register (comma-separated) beyond flow dependencies.",
    )
    p_run_flow.add_argument(
        "--auto-install",
        action="store_true",
        help="pip install missing flow packs via urisys-node pack_resolver (when available).",
    )
    add_runtime_flags(p_run_flow)

    p_mat = msub.add_parser(
        "materialize",
        help="Compile Markpact and unpack to .markpact/{package_id}/ (manifest, handlers, flows, proto).",
    )
    p_mat.add_argument("path", help="Markpact path (optional #flow.id ignored).")
    p_mat.add_argument("--root", default=".markpact", help="Output root directory (default: .markpact).")
    p_mat.add_argument("--force", action="store_true")
    p_mat.add_argument(
        "--platforms",
        default="linux,server,esp32",
        help="Comma-separated platforms for generated/{platform}/ resolver (default: linux,server,esp32).",
    )
    p_mat.add_argument(
        "--no-platform-export",
        action="store_true",
        help="Skip writing generated/{linux,server,esp32}/ under materialized dir.",
    )

    p_export = msub.add_parser(
        "export-platform",
        help="Generate generated/{platform}/urisys.runtime.yaml (+ esp32 uri_routes.h) from a process Markpact.",
    )
    p_export.add_argument("path", help="UriProcess Markpact path.")
    p_export.add_argument("--out", default="generated", help="Output root (default: generated).")
    p_export.add_argument(
        "--platforms",
        default="linux,server,esp32",
        help="Comma-separated: linux, server, esp32.",
    )

    p_run = msub.add_parser(
        "run",
        help="Unpack to .markpact/ and run (pack|service|flow|interface|adapter per markpact:run or --as).",
    )
    p_run.add_argument("path", help="Markpact path (optional #flow.id for flow mode).")
    p_run.add_argument("--as", dest="run_mode", default=None, help="Override mode: pack|service|flow|interface|adapter.")
    p_run.add_argument("--out", default=".markpact", help="Unpack root (default: .markpact).")
    p_run.add_argument("--host", default="0.0.0.0")
    p_run.add_argument("--port", type=int, default=None)
    p_run.add_argument("--config", default=None, help="Optional runtime config YAML.")
    p_run.add_argument("--force", action="store_true", help="Force recompile/unpack.")
    p_run.add_argument(
        "--auto-install",
        action="store_true",
        help="pip install missing flow packs via urisys-node pack_resolver (flow mode).",
    )
    add_runtime_flags(p_run)

    p_pack = msub.add_parser(
        "pack",
        help="Generate a complete self-contained Markpact (definitions + full source + run config) for a uri* package.",
    )
    p_pack.add_argument("package", help="Package name or path (dir holding <pkg>/manifest.yaml).")
    p_pack.add_argument("--out", default=None, help="Write here (default: <pkg>/<pkg>.markpact.md).")
    p_pack.add_argument("--scheme", default=None, help="For multi-scheme packages, which scheme to emit (one pack file per scheme).")
    p_pack.add_argument("--port", type=int, default=8790, help="Default service port written into markpact:run.")
    p_pack.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    p_pack.add_argument("--stdout", action="store_true", help="Print to stdout instead of writing a file.")

    return parser
