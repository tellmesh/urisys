from __future__ import annotations

from .adapter import AdapterMode
from .flow import FlowMode
from .interface import InterfaceMode
from .pack import PackMode
from .service import ServiceMode

RUN_MODES = {
    "adapter": AdapterMode(),
    "flow": FlowMode(),
    "pack": PackMode(),
    "interface": InterfaceMode(),
    "service": ServiceMode(),
}

__all__ = ["RUN_MODES"]
