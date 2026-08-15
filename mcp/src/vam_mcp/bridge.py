from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .paths import bridge_dir, vam_root


class BridgeError(RuntimeError):
    pass


def status() -> dict[str, Any]:
    path = bridge_dir() / "status.json"
    if not path.is_file():
        return {
            "plugin": "missing",
            "ok": False,
            "error": (
                "Plugin status file not found. Load VamMcpBridge as a Session Plugin "
                f"and keep VAM running. Expected {path}"
            ),
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"plugin": "invalid", "ok": False, "error": f"status.json is not valid JSON: {exc}"}
    data["ok"] = True
    data["vamRoot"] = str(vam_root())
    return data


def call(op: str, timeout: float = 20.0, **args: Any) -> dict[str, Any]:
    folder = bridge_dir()
    command_path = folder / "command.json"
    result_path = folder / "result.json"
    cmd_id = uuid.uuid4().hex
    payload = {"id": cmd_id, "op": op}
    payload.update(args)

    if result_path.exists():
        try:
            result_path.unlink()
        except OSError:
            pass

    _atomic_write(command_path, payload)

    deadline = time.time() + timeout
    last_error = "timed out waiting for the VAM plugin"
    while time.time() < deadline:
        if result_path.is_file():
            try:
                data = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                time.sleep(0.05)
                continue
            if str(data.get("id")) != cmd_id:
                time.sleep(0.05)
                continue
            if str(data.get("ok")).lower() in {"false", "0"}:
                raise BridgeError(str(data.get("error") or "plugin returned ok=false"))
            return data
        time.sleep(0.05)

    raise BridgeError(
        f"{last_error} ({op}). Is VamMcpBridge loaded as a Session Plugin and is VAM in the foreground?"
    )


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
