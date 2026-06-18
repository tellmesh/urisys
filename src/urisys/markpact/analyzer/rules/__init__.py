from __future__ import annotations

from .pack import MP009ProcessRequiresSchemes, MP010RequiresCapabilitiesNamespaced
from .capabilities import (
    MP001NamespacedOperation,
    MP002QueryKind,
    MP003CommandKind,
    MP004CommandApproval,
    MP005ProcessHandler,
)
from .flows import MP007ProcessExpect, MP008ImplicitLatest
from .schemes import MP006UndeclaredScheme

MARKPACT_RULES = (
    MP001NamespacedOperation(),
    MP002QueryKind(),
    MP003CommandKind(),
    MP004CommandApproval(),
    MP005ProcessHandler(),
    MP006UndeclaredScheme(),
    MP007ProcessExpect(),
    MP008ImplicitLatest(),
    MP009ProcessRequiresSchemes(),
    MP010RequiresCapabilitiesNamespaced(),
)

__all__ = ["MARKPACT_RULES"]
