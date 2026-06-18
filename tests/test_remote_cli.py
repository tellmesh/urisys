"""urisys remote delegates to urisysnode.remote."""

from __future__ import annotations

from unittest.mock import patch


def test_parser_has_remote_subcommand():
    from urisys.cli.parser import build_parser

    parser = build_parser()
    args = parser.parse_args(["remote", "health", "--endpoint", "http://127.0.0.1:8790"])
    assert args.command == "remote"
    assert args.remote_argv == ["health", "--endpoint", "http://127.0.0.1:8790"]


def test_parser_node_remote_alias():
    from urisys.cli.parser import build_parser

    parser = build_parser()
    args = parser.parse_args(["node", "remote", "restart", "--endpoint", "http://127.0.0.1:8790"])
    assert args.command == "node"
    assert args.node_command == "remote"
    assert args.remote_argv == ["restart", "--endpoint", "http://127.0.0.1:8790"]


def test_cmd_remote_delegates():
    from urisys.cli.commands.remote import cmd_remote

    class Args:
        remote_argv = ["--", "health"]

    with patch("urisysnode.remote.main", return_value=0) as remote_main:
        assert cmd_remote(Args()) == 0
        remote_main.assert_called_once_with(["health"])


def test_remote_help_smoke(capsys):
    from urisys.cli.main import main

    assert main(["remote"]) == 0
    out = capsys.readouterr().out
    assert "health" in out
    assert "restart" in out
