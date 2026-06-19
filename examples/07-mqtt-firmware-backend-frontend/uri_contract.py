from __future__ import annotations

DEVICE_ID = "device-01"


def device_uris(device_id: str = DEVICE_ID) -> dict[str, str]:
    return {
        "events_recent": f"mqtt://{device_id}/events/query/recent",
        "led_set": f"mqtt://{device_id}/led/command/set",
        "ping_send": f"mqtt://{device_id}/ping/command/send",
        "state_current": f"mqtt://{device_id}/state/query/current",
        "telemetry_latest": f"mqtt://{device_id}/telemetry/query/latest",
        "topics_list": f"mqtt://{device_id}/topics/query/list",
    }


def mqtt_topics(device_id: str = DEVICE_ID) -> dict[str, str]:
    base = f"urisys/example/{device_id}"
    return {
        "command_led": f"{base}/command/led",
        "command_ping": f"{base}/command/ping",
        "event": f"{base}/event",
        "state": f"{base}/state",
        "telemetry": f"{base}/telemetry",
    }


def command_topic_for_uri(uri: str, device_id: str = DEVICE_ID) -> str | None:
    uris = device_uris(device_id)
    topics = mqtt_topics(device_id)
    if uri == uris["led_set"]:
        return topics["command_led"]
    if uri == uris["ping_send"]:
        return topics["command_ping"]
    return None


def query_kind_for_uri(uri: str, device_id: str = DEVICE_ID) -> str | None:
    uris = device_uris(device_id)
    return {
        uris["events_recent"]: "events",
        uris["state_current"]: "state",
        uris["telemetry_latest"]: "telemetry",
        uris["topics_list"]: "topics",
    }.get(uri)
