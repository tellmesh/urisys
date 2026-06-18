from __future__ import annotations

from pathlib import Path

from ..helpers import print_json, resolve_markpact_source


def cmd_run_flow(args, manager, source_manager) -> int:
    from ...managers.markpact_run_flow import run_markpact_flow, split_flow_ref

    base, flow_id = split_flow_ref(args.path)
    local = resolve_markpact_source(base, source_manager=source_manager)
    result = run_markpact_flow(
        local, flow_id=flow_id, manager=manager, out_dir=args.out, force=args.force,
        extra_packs=args.extra_packs or None, auto_install=args.auto_install,
        events_path=args.events, approved=args.approve, dry_run=args.dry_run,
        allow_real=args.allow_real, environment=args.environment,
    )
    print_json(result)
    return 0 if result.get("ok") else 1


def cmd_materialize(args, manager, source_manager) -> int:
    from ...managers.markpact_materialize import materialize_markpact
    from ...managers.markpact_run_flow import split_flow_ref

    base, _ = split_flow_ref(args.path)
    local = resolve_markpact_source(base, source_manager=source_manager)
    platforms = [p.strip() for p in str(args.platforms).split(",") if p.strip()]
    print_json(materialize_markpact(local, root=args.root, manager=manager, force=args.force, platforms=platforms, export_platforms=not args.no_platform_export))
    return 0


def cmd_export_platform(args, source_manager) -> int:
    from ...managers.markpact_run_flow import split_flow_ref
    from ...markpact.platform_export import export_platform_artifacts

    base, _ = split_flow_ref(args.path)
    local = resolve_markpact_source(base, source_manager=source_manager)
    platforms = [p.strip() for p in str(args.platforms).split(",") if p.strip()]
    print_json(export_platform_artifacts(local, out_dir=args.out, platforms=platforms))
    return 0


def cmd_run_markpact(args, source_manager) -> int:
    from ...managers.markpact_run import run_markpact
    from ...managers.markpact_run_flow import split_flow_ref

    base, flow_id = split_flow_ref(args.path)
    local = resolve_markpact_source(base, source_manager=source_manager)
    result = run_markpact(local, mode=args.run_mode, flow_id=flow_id, out=args.out, host=args.host, port=args.port, config_path=args.config, approve=args.approve, dry_run=args.dry_run, auto_install=args.auto_install)
    print_json(result)
    return 0 if result.get("ok", True) else 1


def cmd_validate(manager, local_path) -> int:
    print_json(manager.validate(local_path))
    return 0


def cmd_compile(manager, local_path, args) -> int:
    compiled = manager.compile(local_path, out_dir=args.out, force=args.force)
    print_json({"ok": True, "compiled": compiled.to_dict()})
    return 0


def cmd_routes(manager, local_path, args) -> int:
    from uri_control import CapabilityRegistry

    compiled = manager.compile(local_path, out_dir=args.out)
    registry = CapabilityRegistry.from_manifest_files([compiled.manifest_path])
    print_json({
        "ok": True,
        "compiled": compiled.to_dict(),
        "routes": [{"manifest_id": r.manifest_id, "scheme": r.scheme, "pattern": r.pattern, "kind": r.kind, "operation": r.operation, "approval": r.approval, "side_effects": r.side_effects, "handler_ref": r.handler_ref} for r in registry.routes],
    })
    return 0


def cmd_test(manager, local_path, args) -> int:
    print_json(manager.run_tests(local_path, events_path=args.events))
    return 0


def _apply_strict_operations(result: dict[str, Any], warnings: list[str]) -> tuple[dict[str, Any], list[str]]:
    op_warnings = [w for w in warnings if "should be namespaced" in w]
    if not op_warnings:
        return result, warnings
    return {
        **result, "ok": False, "strict_operations": True,
        "errors": list(result.get("errors") or []) + [f"warning: {w}" for w in op_warnings],
    }, [w for w in warnings if w not in op_warnings]


def _apply_strict_profile(result: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    if not warnings:
        return result
    return {
        **result, "ok": False, "strict": True,
        "errors": list(result.get("errors") or []) + [f"warning: {w}" for w in warnings],
    }


def cmd_analyze(manager, local_path, args) -> int:
    from ...markpact.analyzer import analyze_json_report

    result = manager.analyze(local_path)
    warnings = list(result.get("warnings") or [])
    if getattr(args, "strict_operations", False):
        result, warnings = _apply_strict_operations(result, warnings)
    if getattr(args, "strict", False):
        result = _apply_strict_profile(result, warnings)
    if getattr(args, "json", False):
        result = analyze_json_report(result)
    print_json(result)
    return 0 if result.get("ok") else 1


def cmd_pack(args) -> int:
    from ...managers.markpact_pack_gen import find_package_dir, generate_pack_markpact

    rendered = generate_pack_markpact(args.package, port=args.port, scheme=args.scheme)
    if args.stdout:
        print(rendered)
        return 0
    if args.out:
        out = Path(args.out)
    else:
        pkg_dir = find_package_dir(args.package)
        suffix = f".{args.scheme}" if args.scheme else ""
        out = pkg_dir.parent / f"{pkg_dir.name}{suffix}.markpact.md"
    if out.exists() and not args.force:
        print_json({"ok": False, "error": f"{out} exists; use --force to overwrite."})
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print_json({"ok": True, "package": args.package, "markpact": str(out)})
    return 0


def cmd_contract(args, source_manager) -> int:
    from ...managers import contract_gen

    manifest = contract_gen.load_manifest(args.manifest)
    if args.markpact_command == "gen-contract":
        rendered = contract_gen.render_contract_markpact(manifest)
        if args.out:
            out = Path(args.out)
            if out.exists() and not args.force:
                print_json({"ok": False, "error": f"{out} exists; use --force to overwrite."})
                return 2
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered, encoding="utf-8")
            print_json({"ok": True, "manifest": args.manifest, "contract": str(out)})
            return 0
        print(rendered)
        return 0
    contract_path = resolve_markpact_source(args.contract, source_manager=source_manager)
    contract = contract_gen.load_contract_block(contract_path)
    issues = contract_gen.diff_manifest_contract(manifest, contract)
    print_json({
        "ok": not issues,
        "manifest": args.manifest,
        "contract": contract_path,
        "drift": issues,
    })
    return 0 if not issues else 1


def _run_path_command(cmd: str, manager: Any, local_path: Path, args: Any) -> int:
    if cmd == "validate":
        return cmd_validate(manager, local_path)
    if cmd == "compile":
        return cmd_compile(manager, local_path, args)
    if cmd == "routes":
        return cmd_routes(manager, local_path, args)
    if cmd == "test":
        return cmd_test(manager, local_path, args)
    if cmd == "analyze":
        return cmd_analyze(manager, local_path, args)
    return 1


def cmd_markpact(args) -> int:
    from ...managers.markpact_manager import MarkpactManager
    from ...managers.source_manager import SourceManager

    cache_root = getattr(args, "out", None)
    source_manager = SourceManager(cache_root=(Path(args.out) / "sources") if cache_root else ".urisys/cache/sources")
    if args.markpact_command == "fetch":
        print_json(source_manager.fetch(args.source, force=args.force))
        return 0

    manager = MarkpactManager(cache_root=args.out) if cache_root else MarkpactManager()
    if args.markpact_command == "gen-contract":
        return cmd_contract(args, source_manager)
    if args.markpact_command == "check-drift":
        return cmd_contract(args, source_manager)
    if args.markpact_command == "run-flow":
        return cmd_run_flow(args, manager, source_manager)
    if args.markpact_command == "materialize":
        return cmd_materialize(args, manager, source_manager)
    if args.markpact_command == "export-platform":
        return cmd_export_platform(args, source_manager)
    if args.markpact_command == "run":
        return cmd_run_markpact(args, source_manager)
    if args.markpact_command == "pack":
        return cmd_pack(args)

    local_path = resolve_markpact_source(args.path, source_manager=source_manager)
    return _run_path_command(args.markpact_command, manager, local_path, args)
