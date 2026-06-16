"""Test session runners — split from scripts/run_test_sessions.py."""

from __future__ import annotations

from .expectations import evaluate_expectations, flow_expectations
from .lab_flows import session_lab_10_flows
from .lab_rdp import (
    capture_rdp_screenshot,
    capture_rdp_screenshot_wait,
    flow_step_context,
    parse_docker_log_errors,
    parse_lab_flow,
    prepare_ok_target,
    step_pause,
    summarize_uri_response,
)
from .util import (
    ROOT,
    REPORT_SCRIPT,
    compose_cmd,
    copy_container_file,
    copy_host_screenshot,
    docker_logs,
    file_md5,
    finalize_session,
    host_id,
    http_json,
    now_iso,
    prepare_urirdp_data,
    read_meta,
    run_cmd,
    run_id,
    save_json,
    sleep_ports,
    wait_health,
    write_meta,
)

__all__ = [
    "ROOT",
    "REPORT_SCRIPT",
    "capture_rdp_screenshot",
    "capture_rdp_screenshot_wait",
    "compose_cmd",
    "copy_container_file",
    "copy_host_screenshot",
    "docker_logs",
    "evaluate_expectations",
    "file_md5",
    "finalize_session",
    "flow_expectations",
    "flow_step_context",
    "host_id",
    "http_json",
    "now_iso",
    "parse_docker_log_errors",
    "parse_lab_flow",
    "prepare_ok_target",
    "prepare_urirdp_data",
    "read_meta",
    "run_cmd",
    "run_id",
    "save_json",
    "session_lab_10_flows",
    "sleep_ports",
    "step_pause",
    "summarize_uri_response",
    "wait_health",
    "write_meta",
]

# Backward-compatible private aliases
_flow_expectations = flow_expectations
_now_iso = now_iso
_run_id = run_id
_host_id = host_id
_http_json = http_json
_wait_health = wait_health
_compose_cmd = compose_cmd
_prepare_urirdp_data = prepare_urirdp_data
_sleep_ports = sleep_ports
_save_json = save_json
_run_cmd = run_cmd
_write_meta = write_meta
_read_meta = read_meta
_finalize_session = finalize_session
_docker_logs = docker_logs
_copy_container_file = copy_container_file
_copy_host_screenshot = copy_host_screenshot
_file_md5 = file_md5
_parse_lab_flow = parse_lab_flow
_flow_step_context = flow_step_context
_step_pause = step_pause
_summarize_uri_response = summarize_uri_response
_parse_docker_log_errors = parse_docker_log_errors
_prepare_ok_target = prepare_ok_target
_capture_rdp_screenshot = capture_rdp_screenshot
_capture_rdp_screenshot_wait = capture_rdp_screenshot_wait
