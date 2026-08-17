from __future__ import annotations

import json
from typing import Any

from . import bridge
from .paths import vam_root


def _fallback_vap(person: str, locked: bool) -> dict[str, Any]:
    storables: list[dict[str, Any]] = [
        {
            "id": "headControl",
            "positionState": "On" if locked else "On",
            "rotationState": "On" if locked else "On",
        },
        {
            "id": "neckControl",
            "positionState": "On" if locked else "Off",
            "rotationState": "On" if locked else "Off",
        },
        {
            "id": "Eyes",
            "lookMode": "Target" if locked else "Player",
        },
    ]
    if locked:
        for i in range(16):
            for suffix in ("Glance", "vamX.Glance", "Easy Gaze 1.1", "EasyGaze"):
                storables.append(
                    {
                        "id": "plugin#" + str(i) + "_" + suffix,
                        "DisableAutoTarget": "true",
                        "PlayerEyesWeight": "0",
                        "WindowCameraWeight": "0",
                    }
                )
    dest = vam_root() / "Custom" / "Atom" / "Person" / "Pose" / "Preset_VamMcp_HeadLock.vap"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(
            {"setUnlistedParamsToDefault": "false", "storables": storables},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    rel = dest.relative_to(vam_root()).as_posix()
    args: dict[str, Any] = {"path": rel}
    if person:
        args["person"] = person
    result = bridge.call("load_pose", timeout=45.0, **args)
    data = result.get("data") or result
    if not isinstance(data, dict):
        data = {"data": data}
    data["locked"] = locked
    data["fallback"] = "vap"
    data["path"] = rel
    return data


def lock_head(person: str = "", locked: bool = True) -> dict[str, Any]:
    args: dict[str, Any] = {"locked": locked}
    if person:
        args["person"] = person
    try:
        result = bridge.call("lock_head", timeout=15.0, **args)
        data = result.get("data") or result
        if not isinstance(data, dict):
            data = {"data": data}
        return data
    except bridge.BridgeError as exc:
        if "unknown op" not in str(exc).lower():
            raise
        data = _fallback_vap(person, locked)
        data["reloadHint"] = (
            "VamMcpBridge is older than 0.5.1. Applied a keep-flag pose vap. "
            "Reload the Session Plugin to disable Glance/look-at on the person."
        )
        return data
