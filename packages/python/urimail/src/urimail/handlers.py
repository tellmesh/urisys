from __future__ import annotations

from typing import Any

from .common import mock_result, var

_DRAFTS: dict[str, dict[str, Any]] = {}


def create_draft(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    account = var(context, "account", "default")
    draft_id = str(payload.get("draft_id") or f"draft-{len(_DRAFTS) + 1}")
    draft = {
        "draft_id": draft_id,
        "account": account,
        "to": payload.get("to", ""),
        "subject": payload.get("subject", ""),
        "body": payload.get("body", ""),
    }
    _DRAFTS[draft_id] = draft
    return mock_result("mail.create_draft", context, **draft)


def send_draft(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(payload.get("draft_id") or "")
    draft = _DRAFTS.get(draft_id, {"draft_id": draft_id, "account": var(context, "account")})
    return mock_result("mail.send_draft", context, **draft, sent=True, message_id=f"mock-message-{draft_id or '1'}")


def inbox(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    limit = int(payload.get("limit") or 10)
    return mock_result("mail.inbox", context, account=var(context, "account"), messages=[], limit=limit)
