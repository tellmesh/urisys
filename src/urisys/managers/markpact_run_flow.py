"""Compile a showcase Markpact and run an embedded ``markpact:flow`` on uri_control.edge."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from uri_control.edge.compose import build_runtime
from uri_control.edge.runtime import run_flow

from ..defaults import DEFAULT_ENVIRONMENT
from .markpact_flows import classify_flow, declared_uses, _provider_scheme
from .markpact_pack_deps import ensure_flow_packs
from .markpact_manager import MarkpactManager
from .markpact_models import CompiledMarkpact, MarkpactError, safe_identifier

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def split_flow_ref(value: str) -> tuple[str, str | None]:
    """Split ``path/to/pack.markpact.md#flow-id`` into path and optional flow id."""
    if "#" not in value:
        return value, None
    base, fragment = value.rsplit("#", 1)
    return base, (fragment.strip() or None)


def pick_flow_id(compiled: CompiledMarkpact, flow_id: str | None) -> str:
    ids = list(compiled.flow_ids)
    if not ids:
        raise MarkpactError("Markpact has no embedded markpact:flow blocks.")
    if flow_id:
        if flow_id not in ids:
            raise MarkpactError(f"Unknown flow {flow_id!r}; available: {', '.join(ids)}")
        return flow_id
    if len(ids) == 1:
        return ids[0]
    raise MarkpactError(
        f"Multiple embedded flows ({', '.join(ids)}); specify #flow.id in the path argument."
    )


def flow_path_for(compiled: CompiledMarkpact, flow_id: str) -> Path:
    if not compiled.flows_dir:
        raise MarkpactError("Compiled Markpact has no flows directory.")
    path = compiled.flows_dir / f"{safe_identifier(flow_id, fallback='flow')}.uri.flow.yaml"
    if not path.is_file():
        raise MarkpactError(f"Compiled flow file missing: {path}")
    return path


def packs_for_flow(
    pack: dict[str, Any],
    flow_data: dict[str, Any],
    *,
    pack_scheme: str,
    extra: str | Iterable[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Return (pack aliases to load, undeclared foreign schemes) for one flow."""
    declared = declared_uses(pack)
    info = classify_flow(flow_data, pack_scheme=pack_scheme, declared_uses=declared)
    names = sorted({_provider_scheme(s) for s in info["foreign_schemes"]})
    for item in _split_extra(extra):
        if item not in names:
            names.append(item)
    return sorted(names), list(info["undeclared_uses"])


def _split_extra(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [p.strip() for p in value.split(",") if p.strip()]
    return [str(p).strip() for p in value if str(p).strip()]


def run_markpact_flow(
    path: str | Path,
    *,
    flow_id: str | None = None,
    manager: MarkpactManager | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
    extra_packs: str | Iterable[str] | None = None,
    auto_install: bool = False,
    events_path: str | Path = ".urisys/cache/markpact-flow-events.jsonl",
    approved: bool = False,
    dry_run: bool = False,
    allow_real: bool = False,
    environment: str = DEFAULT_ENVIRONMENT,
) -> dict[str, Any]:
    """Compile *path*, build edge runtime (manifest + flow deps), run one flow."""
    mgr = manager or MarkpactManager()
    path_text, inline_flow = split_flow_ref(str(path))
    if flow_id is None:
        flow_id = inline_flow
    source_path = Path(path_text)
    compiled = mgr.compile(source_path, out_dir=out_dir, force=force)
    pack = mgr.load_pack_block(source_path)
    chosen = pick_flow_id(compiled, flow_id)
    flow_file = flow_path_for(compiled, chosen)
    if yaml is None:  # pragma: no cover
        raise MarkpactError("PyYAML is required to run markpact flows.")
    flow_data = yaml.safe_load(flow_file.read_text(encoding="utf-8")) or {}
    pack_scheme = mgr._scheme(pack, mgr._capabilities(pack))
    uses, undeclared = packs_for_flow(pack, flow_data, pack_scheme=pack_scheme, extra=extra_packs)
    if undeclared:
        raise MarkpactError(
            f"Flow {chosen!r} uses schemes not declared in pack uses: {undeclared}"
        )

    install_report: dict[str, Any] | None = None
    if uses:
        install_report = ensure_flow_packs(uses, anchor=source_path, auto_install=auto_install)

    packs_arg = ",".join(uses) if uses else None
    try:
        rt = build_runtime(
            packs=packs_arg,
            manifests=[str(compiled.manifest_path)],
            events_path=events_path,
        )
    except ModuleNotFoundError as exc:
        raise MarkpactError(
            f"Missing pack module for flow dependencies: {exc}. "
            f"Flow packs: {uses or []}. Set TELLMESH_ROOT, use --auto-install, or pass --extra-packs."
        ) from exc

    context: dict[str, Any] = {"environment": environment}
    if approved:
        context["approved"] = True
    if dry_run:
        context["dry_run"] = True
    if allow_real:
        context["allow_real"] = True

    results = run_flow(rt, str(flow_file), context)
    ok = all(r.get("ok") for r in results)
    return {
        "ok": ok,
        "flow_id": chosen,
        "flow_path": str(flow_file),
        "uses": uses,
        "install": install_report,
        "compiled": compiled.to_dict(),
        "results": results,
    }


__all__ = [
    "split_flow_ref",
    "pick_flow_id",
    "flow_path_for",
    "packs_for_flow",
    "run_markpact_flow",
]
