from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class StepperDriver:
    def status(self, device: str, axis: str, cfg: dict) -> dict:
        raise NotImplementedError

    def enable(self, device: str, axis: str, cfg: dict) -> dict:
        raise NotImplementedError

    def disable(self, device: str, axis: str, cfg: dict) -> dict:
        raise NotImplementedError

    def stop(self, device: str, axis: str, cfg: dict) -> dict:
        raise NotImplementedError

    def move_relative(self, device: str, axis: str, cfg: dict, steps: int, direction: str, speed_sps: float) -> dict:
        raise NotImplementedError

    def move_absolute(self, device: str, axis: str, cfg: dict, position: int, speed_sps: float) -> dict:
        current = int(self.status(device, axis, cfg).get("position_steps", 0))
        delta = position - current
        direction = "cw" if delta >= 0 else "ccw"
        return self.move_relative(device, axis, cfg, abs(delta), direction, speed_sps) | {"target_position_steps": position}

    def home(self, device: str, axis: str, cfg: dict, direction: str, speed_sps: float) -> dict:
        # Simple demo: mock home resets position. Real implementation should use a limit switch.
        raise NotImplementedError


class MockStepperDriver(StepperDriver):
    def __init__(self, state_path: str | os.PathLike[str] | None = None):
        self.path = Path(state_path or os.environ.get("URISYS_STATE_PATH", "/tmp/stepper_state.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def _key(self, device: str, axis: str) -> str:
        return f"{device}:{axis}"

    def _axis(self, device: str, axis: str) -> dict:
        data = self._load()
        key = self._key(device, axis)
        item = data.setdefault(key, {"enabled": False, "position_steps": 0, "moving": False, "driver": "mock"})
        self._save(data)
        return item

    def _update(self, device: str, axis: str, changes: dict) -> dict:
        data = self._load()
        key = self._key(device, axis)
        item = data.setdefault(key, {"enabled": False, "position_steps": 0, "moving": False, "driver": "mock"})
        item.update(changes)
        self._save(data)
        return item

    def status(self, device: str, axis: str, cfg: dict) -> dict:
        item = self._axis(device, axis)
        return item | {"device": device, "axis": axis, "config_driver": cfg.get("driver", "mock")}

    def enable(self, device: str, axis: str, cfg: dict) -> dict:
        return self._update(device, axis, {"enabled": True, "driver": cfg.get("driver", "mock")}) | {"device": device, "axis": axis}

    def disable(self, device: str, axis: str, cfg: dict) -> dict:
        return self._update(device, axis, {"enabled": False, "moving": False}) | {"device": device, "axis": axis}

    def stop(self, device: str, axis: str, cfg: dict) -> dict:
        return self._update(device, axis, {"moving": False}) | {"device": device, "axis": axis, "stopped": True}

    def move_relative(self, device: str, axis: str, cfg: dict, steps: int, direction: str, speed_sps: float) -> dict:
        state = self._axis(device, axis)
        pos = int(state.get("position_steps", 0))
        delta = steps if direction == "cw" else -steps
        # Simulate a tiny amount of elapsed time, but avoid slow tests.
        time.sleep(min(0.02, steps / max(speed_sps, 1.0) / 1000.0))
        item = self._update(device, axis, {"position_steps": pos + delta, "moving": False, "last_speed_sps": speed_sps, "enabled": True})
        return item | {"device": device, "axis": axis, "steps": steps, "direction": direction, "driver": "mock"}

    def move_absolute(self, device: str, axis: str, cfg: dict, position: int, speed_sps: float) -> dict:
        current = int(self.status(device, axis, cfg).get("position_steps", 0))
        direction = "cw" if position >= current else "ccw"
        steps = abs(position - current)
        return self.move_relative(device, axis, cfg, steps, direction, speed_sps) | {"target_position_steps": position}

    def home(self, device: str, axis: str, cfg: dict, direction: str, speed_sps: float) -> dict:
        item = self._update(device, axis, {"position_steps": 0, "moving": False, "enabled": True, "homed": True})
        return item | {"device": device, "axis": axis, "direction": direction, "speed_sps": speed_sps, "driver": "mock"}


class RpiGpioStepDirDriver(StepperDriver):
    def __init__(self):
        try:
            from gpiozero import DigitalOutputDevice  # type: ignore
        except Exception as exc:
            raise RuntimeError("gpiozero is required for driver=rpi-gpio-step-dir. Use driver=mock in Docker.") from exc
        self._DigitalOutputDevice = DigitalOutputDevice
        self._axes = {}

    def _pins(self, axis: str, cfg: dict):
        key = axis
        if key not in self._axes:
            D = self._DigitalOutputDevice
            self._axes[key] = {
                "step": D(int(cfg["step_pin"])),
                "dir": D(int(cfg["dir_pin"])),
                "enable": D(int(cfg["enable_pin"])) if cfg.get("enable_pin") is not None else None,
            }
        return self._axes[key]

    def _enable_value(self, cfg: dict, enabled: bool) -> bool:
        active_low = bool(cfg.get("enable_active_low", True))
        return (not enabled) if active_low else enabled

    def status(self, device: str, axis: str, cfg: dict) -> dict:
        return {"device": device, "axis": axis, "driver": "rpi-gpio-step-dir", "position_steps": None, "enabled": None}

    def enable(self, device: str, axis: str, cfg: dict) -> dict:
        pins = self._pins(axis, cfg)
        if pins["enable"]:
            pins["enable"].value = self._enable_value(cfg, True)
        return {"device": device, "axis": axis, "enabled": True, "driver": "rpi-gpio-step-dir"}

    def disable(self, device: str, axis: str, cfg: dict) -> dict:
        pins = self._pins(axis, cfg)
        if pins["enable"]:
            pins["enable"].value = self._enable_value(cfg, False)
        return {"device": device, "axis": axis, "enabled": False, "driver": "rpi-gpio-step-dir"}

    def stop(self, device: str, axis: str, cfg: dict) -> dict:
        return {"device": device, "axis": axis, "stopped": True, "driver": "rpi-gpio-step-dir"}

    def move_relative(self, device: str, axis: str, cfg: dict, steps: int, direction: str, speed_sps: float) -> dict:
        pins = self._pins(axis, cfg)
        if pins["enable"]:
            pins["enable"].value = self._enable_value(cfg, True)
        pins["dir"].value = 1 if direction == "cw" else 0
        pulse_us = int(cfg.get("min_pulse_us", 5))
        low_delay = max(1.0 / max(speed_sps, 1.0), pulse_us / 1_000_000 * 2)
        for _ in range(steps):
            pins["step"].on()
            time.sleep(pulse_us / 1_000_000)
            pins["step"].off()
            time.sleep(low_delay)
        return {"device": device, "axis": axis, "steps": steps, "direction": direction, "speed_sps": speed_sps, "driver": "rpi-gpio-step-dir"}

    def home(self, device: str, axis: str, cfg: dict, direction: str, speed_sps: float) -> dict:
        raise RuntimeError("home requires limit-switch support; not implemented in minimal RPi driver")


def make_driver(driver_name: str) -> StepperDriver:
    if driver_name in ("mock", "mock-stepper"):
        return MockStepperDriver()
    if driver_name in ("rpi-gpio-step-dir", "rpi_gpio_step_dir"):
        return RpiGpioStepDirDriver()
    raise RuntimeError(f"Unsupported stepper driver: {driver_name}")
