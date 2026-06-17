from urimail.handlers import inbox_unread, message_compose, message_send, status as mail_status
from urioffice.handlers import document_export_pdf, status as office_status, writer_render
from urivql.handlers import ui_compare, ui_detect
from urillm.handlers import text_plan


def _ctx(*, dry_run=True, allow_real=False):
    return {
        "approved": True,
        "dry_run": dry_run,
        "allow_real": allow_real,
        "config": {
            "office": {"driver": "mock", "output_dir": "data/office-test"},
            "mail": {"driver": "mock"},
        },
        "params": {"host": "local", "account": "local"},
    }


def test_office_status_and_writer_render():
    ctx = _ctx(dry_run=True)
    st = office_status({}, ctx)
    assert st["driver"] == "mock"
    rendered = writer_render(
        {"title": "demo", "text": "Hello office", "format": "txt"},
        ctx,
    )
    assert rendered["dry_run"] is True
    assert rendered["chars"] == 12


def test_office_writer_real_export_pdf(tmp_path):
    ctx = _ctx(dry_run=False, allow_real=True)
    ctx["config"]["office"]["output_dir"] = str(tmp_path)
    rendered = writer_render(
        {"title": "demo", "text": "Export me", "format": "txt"},
        ctx,
    )
    assert rendered["rendered"] is True
    exported = document_export_pdf({}, ctx)
    assert exported["exported"] is True
    assert exported["pdf_path"].endswith(".pdf")


def test_mail_unread_compose_send_dry_run():
    ctx = _ctx(dry_run=True)
    st = mail_status({}, ctx)
    assert "mock" in st["supports"]
    unread = inbox_unread({"limit": 2}, ctx)
    assert unread["count"] == 2
    composed = message_compose(
        {"to": "team@example.com", "subject": "Hi", "body": "Draft"},
        ctx,
    )
    assert composed["dry_run"] is True
    sent = message_send({"to": "team@example.com"}, ctx)
    assert sent["dry_run"] is True


def test_vql_detect_compare_mock():
    ctx = _ctx()
    detected = ui_detect({"target": "Example"}, ctx)
    assert detected["source"] == "urivql-mock"
    compared = ui_compare({"expect": {"changed": True}}, ctx)
    assert compared["ok"] is True


def test_plan_mail_scheme():
    result = text_plan(
        {"transcript": "Summarize unread mail and draft a one-line reply", "allowed_schemes": ["urimail"]},
        {"approved": True, "dry_run": False, "allow_real": True},
    )
    assert result["ok"]
    assert result["uri"] == "urimail://local/message/command/compose"


def test_plan_office_scheme():
    result = text_plan(
        {"transcript": "Office writer: produce a short paragraph about quarterly results", "allowed_schemes": ["urioffice"]},
        {"approved": True, "dry_run": False, "allow_real": True},
    )
    assert result["ok"]
    assert result["uri"] == "urioffice://local/writer/command/render"
