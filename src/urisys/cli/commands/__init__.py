from __future__ import annotations

from ..protocol import CliCommand
from .markpact import cmd_markpact
from .node import cmd_node
from .remote import cmd_remote
from .runtime import cmd_events, cmd_flow, cmd_serve, cmd_uri
from .setup import cmd_doctor, cmd_init

COMMAND_HANDLERS: dict[str, CliCommand] = {
    "markpact": cmd_markpact,
    "doctor": cmd_doctor,
    "init": cmd_init,
    "serve": cmd_serve,
    "node": cmd_node,
    "remote": cmd_remote,
    "flow": cmd_flow,
    "events": cmd_events,
    "call": cmd_uri,
    "explain": cmd_uri,
    "routes": cmd_uri,
}
