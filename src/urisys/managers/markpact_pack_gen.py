"""Generate a complete, self-contained Markpact for a uri* package.

Introspects an installed-layout package (``<pkg>/<pkg>/`` with ``manifest.yaml``
and handler source) and assembles ONE ``.markpact.md`` carrying everything needed
to unpack and run it standalone:

* ``markpact:pack``    — capability definitions derived from ``manifest.yaml``
* ``markpact:module``  — verbatim source for every ``.py`` (the package tree)
* ``markpact:proto``   — type definitions from ``uricore/contracts/proto/<scheme>/`` (if any)
* ``markpact:run``     — run configuration (modes: pack/service/flow/interface/adapter)
* ``markpact:docs``    — the package README

The pack's handler refs stay ``python://<pkg>.handlers:fn``; the runner writes the
embedded modules as a real ``<pkg>/`` package on ``sys.path`` so those refs (and
internal relative imports) resolve against the embedded code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .contract_gen import normalize_version
from .markpact_models import MarkpactError

API_VERSION = "urisys.io/v1"
DEFAULT_PORT = 8790


def find_package_dir(target: str | Path, *, repo_root: Path | None = None) -> Path:
    """Resolve a package name or path to the inner package dir holding manifest.yaml."""
    p = Path(target)
    candidates: list[Path] = []
    if p.exists() and (p / "manifest.yaml").exists():
        candidates.append(p)
    if p.exists() and (p / p.name / "manifest.yaml").exists():
        candidates.append(p / p.name)
    if repo_root is not None:
        candidates.append(repo_root / str(target) / str(target))
    for c in candidates:
        if (c / "manifest.yaml").exists():
            return c
    raise MarkpactError(f"Could not locate a package with manifest.yaml for {target!r}.")


def _load_manifest(package_dir: Path) -> dict[str, Any]:
    data = yaml.safe_load((package_dir / "manifest.yaml").read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise MarkpactError(f"{package_dir}/manifest.yaml must be a YAML mapping.")
    return data


def package_schemes(manifest: dict[str, Any]) -> list[str]:
    if manifest.get("scheme"):
        return [str(manifest["scheme"])]
    schemes = manifest.get("schemes") or []
    if isinstance(schemes, list) and schemes:
        return [str(s) for s in schemes]
    # last resort: infer from patterns
    seen: list[str] = []
    for item in manifest.get("uri_patterns") or []:
        pat = str(item.get("pattern") or "")
        if "://" in pat and pat.split("://", 1)[0] not in seen:
            seen.append(pat.split("://", 1)[0])
    return seen


def _pack_block(manifest: dict[str, Any], pkg_name: str, scheme: str) -> dict[str, Any]:
    handlers = (manifest.get("handlers") or {}).get("python") or {}
    capabilities = []
    for item in manifest.get("uri_patterns") or []:
        operation = str(item.get("operation") or "")
        pattern = str(item.get("pattern") or "")
        if "://" in pattern and pattern.split("://", 1)[0] != scheme:
            continue  # one scheme per pack file
        kind = str(item.get("kind") or ("command" if "/command/" in pattern else "query"))
        handler = handlers.get(operation) or f"python://{pkg_name}.handlers:{operation.split('.')[-1]}"
        cap = {
            "id": operation,
            "uri": pattern,
            "kind": kind,
            "operation": operation,
            "handler": handler,
            "side_effects": bool(item.get("side_effects", kind == "command")),
            "approval": str(item.get("approval", "required" if kind == "command" else "not_required")),
        }
        for opt in ("command_type", "query_type", "result_type", "success_event_type", "description"):
            if opt in item:
                cap[opt] = item[opt]
        capabilities.append(cap)

    pack: dict[str, Any] = {
        "apiVersion": API_VERSION,
        "kind": "UriPack",
        "metadata": {
            "id": f"{manifest.get('id', pkg_name)}-pack",
            "version": normalize_version(manifest.get("version")),
            "language": "python",
        },
        "description": str(manifest.get("description") or f"{pkg_name} URI pack."),
        "schemes": [scheme],
    }
    uses = manifest.get("uses")
    if isinstance(uses, list) and uses:
        pack["uses"] = list(uses)
    pack["capabilities"] = capabilities
    pack["policy"] = {"default": "deny_mutations_without_approval"}
    pack["runtime"] = {"default_environment": "mock", "supports": ["mock", "local", "docker"]}
    return pack


def _run_block(scheme: str, flow_ids: list[str], port: int) -> dict[str, Any]:
    return {
        "modes": ["pack", "service", "flow", "interface", "adapter"],
        "default": "service",
        "scheme": scheme,
        "service": {"port": port, "wire": "POST /uri/call"},
        "flow": {"ids": flow_ids},
        "adapter": {"wire": "POST /uri/call", "events": "GET /events"},
    }


def _module_blocks(package_dir: Path, pkg_name: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for py in sorted(package_dir.rglob("*.py")):
        rel = py.relative_to(package_dir).as_posix()
        path = f"{pkg_name}/{rel}"
        content = py.read_text(encoding="utf-8")
        if "```" in content:
            raise MarkpactError(f"{py} contains triple backticks; cannot embed verbatim.")
        blocks.append((path, content))
    return blocks


def _proto_blocks(repo_root: Path, scheme: str) -> list[tuple[str, str]]:
    proto_root = repo_root / "uricore" / "contracts" / "proto" / scheme
    if not proto_root.is_dir():
        return []
    out: list[tuple[str, str]] = []
    for proto in sorted(proto_root.rglob("*.proto")):
        rel = proto.relative_to(repo_root / "uricore" / "contracts" / "proto").as_posix()
        out.append((rel, proto.read_text(encoding="utf-8")))
    return out


def _sanitize_docs(text: str) -> str:
    # Replace ``` fences so embedded README cannot terminate the docs block early.
    return text.replace("```", "~~~")


def _embedded_flows(repo_root: Path, scheme: str, limit: int = 2) -> list[tuple[str, str]]:
    """Find a few example flows that reference this scheme; return (id, raw_yaml)."""
    examples = repo_root / "tellmesh" / "examples"
    found: list[tuple[str, str]] = []
    if not examples.is_dir():
        return found
    needle = f"{scheme}://"
    for flow in sorted(examples.rglob("*.uri.flow.yaml")):
        text = flow.read_text(encoding="utf-8")
        if needle not in text or "```" in text:
            continue
        data = yaml.safe_load(text) or {}
        fid = (data.get("flow") or {}).get("id") or flow.stem
        found.append((str(fid), text))
        if len(found) >= limit:
            break
    return found


def generate_pack_markpact(
    target: str | Path, *, repo_root: Path | None = None, port: int = DEFAULT_PORT, scheme: str | None = None
) -> str:
    package_dir = find_package_dir(target, repo_root=repo_root)
    pkg_name = package_dir.name
    repo_root = repo_root or package_dir.parents[1]
    manifest = _load_manifest(package_dir)
    schemes = package_schemes(manifest)
    if not schemes:
        raise MarkpactError("manifest.scheme is required.")
    if scheme is None:
        if len(schemes) > 1:
            raise MarkpactError(
                f"{pkg_name} declares multiple schemes {schemes}; pass --scheme <one> (one pack file per scheme)."
            )
        scheme = schemes[0]
    elif scheme not in schemes:
        raise MarkpactError(f"Scheme {scheme!r} not in package schemes {schemes}.")

    pack = _pack_block(manifest, pkg_name, scheme)
    modules = _module_blocks(package_dir, pkg_name)
    protos = _proto_blocks(repo_root, scheme)
    flows = _embedded_flows(repo_root, scheme)
    run_cfg = _run_block(scheme, [fid for fid, _ in flows], port)

    parts: list[str] = []
    parts.append(f"# UriPack: {pkg_name}\n")
    parts.append(
        "Self-contained Markpact — definitions, full source, run config. "
        "Unpack & run: `urisys markpact run "
        f"{pkg_name}/{pkg_name}.markpact.md --as service` (writes `.markpact/`).\n"
    )
    parts.append("```yaml markpact:pack\n" + yaml.safe_dump(pack, sort_keys=False, allow_unicode=True).rstrip() + "\n```\n")
    parts.append("```yaml markpact:run\n" + yaml.safe_dump(run_cfg, sort_keys=False, allow_unicode=True).rstrip() + "\n```\n")

    for path, content in modules:
        parts.append(f"```python markpact:module path={path}\n{content.rstrip()}\n```\n")
    for path, content in protos:
        parts.append(f"```proto markpact:proto path={path}\n{content.rstrip()}\n```\n")
    for fid, raw in flows:
        parts.append(f"```yaml markpact:flow id={fid}\n{raw.rstrip()}\n```\n")

    readme = package_dir.parent / "README.md"
    if readme.exists():
        parts.append("```markdown markpact:docs\n" + _sanitize_docs(readme.read_text(encoding="utf-8")).rstrip() + "\n```\n")

    return "\n".join(parts) + "\n"
