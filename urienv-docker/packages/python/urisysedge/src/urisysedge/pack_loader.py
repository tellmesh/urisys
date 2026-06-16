from __future__ import annotations
import importlib.util
from pathlib import Path
PACK_MODULES = {"env": "urienv", "gpio": "urigpio", "usb": "uriusb", "stepper": "uristepper"}

def manifest_path_for_pack(pack: str) -> Path:
    module_name = PACK_MODULES.get(pack, pack); spec = importlib.util.find_spec(module_name)
    if spec is None or not spec.origin: raise RuntimeError(f"Cannot find package for pack {pack!r} / module {module_name!r}")
    path = Path(spec.origin).parent / "manifest.yaml"
    if not path.exists(): raise RuntimeError(f"Manifest not found for pack {pack!r}: {path}")
    return path

def manifest_paths(packs: list[str]) -> list[Path]:
    if packs == ["all"]: packs = list(PACK_MODULES.keys())
    return [manifest_path_for_pack(p) for p in packs]
