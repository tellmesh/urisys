from __future__ import annotations


from ..defaults import DEFAULT_ENVIRONMENT


class PolicyManager:
    """Placeholder for stronger policies: RBAC, signed approvals, OPA/Cedar/Casbin."""

    def build_context(self, *, approved=False, dry_run=False, allow_real=False, environment=DEFAULT_ENVIRONMENT, caller="urisys", extra=None) -> dict:
        return {
            "approved": bool(approved),
            "dry_run": bool(dry_run),
            "allow_real": bool(allow_real),
            "environment": environment,
            "caller": caller,
            **(extra or {}),
        }
