"""Generate per-platform resolver stubs from UriProcess Markpacts (Etap 4)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

from .blocks import read_blocks
from .pack import load_pack_block, package_id
from .flows import extract_flows, flow_uris
from .profile import declared_schemes

_AUTHORITY_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")

# scheme → default local adapter on edge-linux (generated stub)
_SCHEME_ADAPTERS: dict[str, str] = {
    "stepper": "uristepper",
    "screen": "uriscreen",
    "tts": "uristt",
    "stt": "uristt",
    "him": "urihim",
    "kvm": "urikvm",
    "ocr": "uriocr",
    "llm": "urillm",
    "rdp": "urirdp",
    "browser": "uribrowserdocker",
    "shell": "urishell",
    "env": "urienv",
}

_PLATFORM_ENV: dict[str, str] = {
    "linux": "edge-linux",
    "server": "server-linux",
    "esp32": "esp32-edge",
}


def _resolve_authority(uri: str, input_defaults: dict[str, Any]) -> str | None:
    if "${" in uri:
        for key, value in input_defaults.items():
            placeholder = "${" + key + "}"
            if placeholder in uri and value is not None:
                resolved = uri.replace(placeholder, str(value))
                host = urlsplit(resolved).netloc
                if host and _AUTHORITY_RE.match(host):
                    return host
        return None
    host = urlsplit(uri).netloc
    return host if host and _AUTHORITY_RE.match(host) else None


def _authorities_from_flow(flow_data: dict[str, Any]) -> set[str]:
    authorities: set[str] = set()
    input_defaults: dict[str, Any] = {}
    inputs_block = flow_data.get("inputs")
    if isinstance(inputs_block, dict):
        for name, spec in inputs_block.items():
            if isinstance(spec, dict) and "default" in spec:
                input_defaults[str(name)] = spec["default"]

    for uri in flow_uris(flow_data):
        host = _resolve_authority(uri, input_defaults)
        if host:
            authorities.add(host)

    for value in input_defaults.values():
        if isinstance(value, str) and _AUTHORITY_RE.match(value):
            authorities.add(value)
    return authorities


def collect_process_uris(path: str | Path) -> dict[str, Any]:
    """Extract URIs, authorities and schemes from embedded process flows."""
    source = Path(path)
    blocks = read_blocks(source)
    pack = load_pack_block(source)
    flows = extract_flows(blocks)

    uris: list[str] = []
    authorities: set[str] = set()
    schemes: set[str] = set()
    for flow in flows:
        data = flow["data"]
        uris.extend(flow_uris(data))
        authorities |= _authorities_from_flow(data)
        for uri in flow_uris(data):
            if "${" in uri:
                continue
            parsed = urlsplit(uri)
            if parsed.scheme:
                schemes.add(parsed.scheme)

    return {
        "path": str(source.resolve()),
        "package_id": package_id(pack, source),
        "flow_ids": [f["id"] for f in flows],
        "uris": uris,
        "authorities": sorted(authorities),
        "schemes": sorted(schemes | declared_schemes(pack)),
        "requires_schemes": sorted(declared_schemes(pack)),
    }


def _target_stub(authority: str, platform: str, schemes: set[str]) -> dict[str, Any]:
    if platform == "esp32":
        if authority in {"local", "operator", "runtime"}:
            adapter = _SCHEME_ADAPTERS.get("screen" if authority == "operator" else "tts", "mock")
            return {"platform": "edge-linux", "transport": "local", "adapter": adapter}
        return {
            "platform": "esp32",
            "transport": "mqtt",
            "endpoint": f"urisys/{authority}/call",
            "options": {"qos": 1, "timeout_ms": 5000},
        }

    if platform == "server":
        if authority == "build":
            return {
                "platform": "server-linux",
                "transport": "ssh",
                "adapter": "urishell",
                "options": {"host": "build.internal", "user": "deploy"},
            }
        return {"platform": "server-linux", "transport": "local", "adapter": "mock"}

    # linux (default edge)
    if authority == "operator":
        return {"platform": "desktop-linux", "transport": "local", "adapter": "uriscreen"}
    if authority == "local":
        return {"platform": "edge-linux", "transport": "local", "adapter": "uristt"}
    if authority == "build":
        return {
            "platform": "server-linux",
            "transport": "ssh",
            "adapter": "urishell",
            "options": {"host": "build.internal", "user": "deploy"},
        }
    if authority in {"machine-01", "tic-t249"} or "stepper" in schemes:
        return {
            "platform": "esp32",
            "transport": "mqtt",
            "endpoint": f"urisys/{authority}/call",
            "options": {"qos": 1, "timeout_ms": 5000},
        }
    return {"platform": "edge-linux", "transport": "local", "adapter": "mock"}


def build_resolver_yaml(
    *,
    platform: str,
    authorities: list[str],
    schemes: list[str],
    package_id: str,
) -> dict[str, Any]:
    """Build a deployment stub ``urisys.runtime.yaml`` for *platform*."""
    env = _PLATFORM_ENV.get(platform, f"{platform}-edge")
    scheme_set = set(schemes)
    targets = {auth: _target_stub(auth, platform, scheme_set) for auth in authorities}

    doc: dict[str, Any] = {
        "apiVersion": "tellmesh.io/v1",
        "kind": "UriRuntimeResolver",
        "metadata": {
            "generated_from": package_id,
            "platform": platform,
            "profile": "uri-resolver/v1",
        },
        "environment": env,
        "targets": targets,
        "runtime": {"default_environment": "mock", "dry_run": True},
    }

    if "package" in scheme_set or "shell" in scheme_set:
        doc["uri_aliases"] = {"package://chromium/command/install": "shell://apt-get"}

    if "stepper" in scheme_set:
        doc["policy"] = {
            "operations": {
                "stepper.move_relative": {"max": {"steps": 10000, "speed_sps": 1200}},
                "*": {"max": {"speed_sps": 2000}},
            }
        }

    return doc


def _esp32_routes_header(uris: list[str], package_id: str) -> str:
    lines = [
        "/* Generated UriProcess route table stub — edit before firmware build. */",
        f"/* package: {package_id} */",
        "#pragma once",
        "",
        "typedef struct { const char *uri_prefix; const char *authority; } uri_route_t;",
        "",
        "static const uri_route_t URI_ROUTES[] = {",
    ]
    seen: set[str] = set()
    for uri in uris:
        if "${" in uri:
            continue
        parsed = urlsplit(uri)
        prefix = f"{parsed.scheme}://{parsed.netloc}/" if parsed.netloc else f"{parsed.scheme}://"
        if prefix in seen:
            continue
        seen.add(prefix)
        auth = parsed.netloc or "local"
        lines.append(f'  {{ "{prefix}", "{auth}" }},')
    lines.extend(["};", f"static const int URI_ROUTES_COUNT = {len(seen)};", ""])
    return "\n".join(lines)


def _server_compose_snippet(package_id: str) -> str:
    return (
        "# Generated docker-compose snippet (stub) — merge into your stack.\n"
        f"# process: {package_id}\n"
        "services:\n"
        "  urisys-edge:\n"
        "    image: tellmesh/urisys-node:latest\n"
        "    ports:\n"
        '      - "${URISYS_PORT:-8790}:8790"\n'
        "    volumes:\n"
        "      - ./generated/server/urisys.runtime.yaml:/etc/urisys/runtime.yaml:ro\n"
    )


def export_platform_artifacts(
    path: str | Path,
    *,
    out_dir: str | Path = "generated",
    platforms: list[str] | tuple[str, ...] | None = None,
    materialized_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Write ``generated/{platform}/urisys.runtime.yaml`` (+ esp32 header) from a process Markpact."""
    collected = collect_process_uris(path)
    if not collected["flow_ids"]:
        return {"ok": False, "error": "no embedded flows", "collected": collected}

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    platform_list = list(platforms or ("linux", "server", "esp32"))
    files: list[str] = []

    for platform in platform_list:
        plat_dir = root / platform
        plat_dir.mkdir(parents=True, exist_ok=True)
        resolver = build_resolver_yaml(
            platform=platform,
            authorities=collected["authorities"],
            schemes=collected["schemes"],
            package_id=collected["package_id"],
        )
        runtime_path = plat_dir / "urisys.runtime.yaml"
        runtime_path.write_text(
            yaml.safe_dump(resolver, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        files.append(str(runtime_path.resolve()))

        if platform == "esp32":
            header = plat_dir / "uri_routes.h"
            header.write_text(
                _esp32_routes_header(collected["uris"], collected["package_id"]),
                encoding="utf-8",
            )
            files.append(str(header.resolve()))

        if platform == "server":
            snippet = plat_dir / "docker-compose.snippet.yml"
            snippet.write_text(_server_compose_snippet(collected["package_id"]), encoding="utf-8")
            files.append(str(snippet.resolve()))

    index = {
        "ok": True,
        "package_id": collected["package_id"],
        "platforms": platform_list,
        "authorities": collected["authorities"],
        "schemes": collected["schemes"],
        "files": files,
        "out_dir": str(root.resolve()),
    }
    if materialized_dir is not None:
        index_path = Path(materialized_dir) / "generated" / "platform-export.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
        files.append(str(index_path.resolve()))
    else:
        index_path = root / "platform-export.json"
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
        files.append(str(index_path.resolve()))

    return index


__all__ = [
    "collect_process_uris",
    "build_resolver_yaml",
    "export_platform_artifacts",
]
