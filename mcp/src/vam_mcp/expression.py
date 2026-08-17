from __future__ import annotations

import json
from typing import Any

from . import bridge
from .paths import vam_root

# One-word aliases -> recipe id
ALIASES: dict[str, str] = {
    "neutral": "neutral",
    "none": "neutral",
    "reset": "neutral",
    "default": "neutral",
    "无表情": "neutral",
    "重置": "neutral",
    "正常": "neutral",
    "ahegao": "ahegao",
    "ahe": "ahegao",
    "上翻吐舌": "ahegao",
    "吐舌上翻": "ahegao",
    "翻白眼吐舌": "ahegao",
    "eyeroll": "eyeroll",
    "eye roll": "eyeroll",
    "eyes roll": "eyeroll",
    "eye-roll": "eyeroll",
    "翻白眼": "eyeroll",
    "上翻": "eyeroll",
    "双眼上翻": "eyeroll",
    "眼上翻": "eyeroll",
    "tongue": "tongue",
    "tongue out": "tongue",
    "吐舌": "tongue",
    "舌头": "tongue",
    "伸舌头": "tongue",
    "舌头吐出来": "tongue",
    "smile": "smile",
    "笑": "smile",
    "微笑": "smile",
    "smile2": "smile2",
    "kiss": "kiss",
    "吻": "kiss",
    "kiss2": "kiss2",
    "kiss3": "kiss3",
    "pleasure": "pleasure",
    "高潮": "pleasure",
    "舒服": "pleasure",
    "angry": "angry",
    "anger": "angry",
    "生气": "angry",
    "怒": "angry",
    "sad": "sad",
    "伤心": "sad",
    "难过": "sad",
    "sad2": "sad2",
    "surprise": "surprise",
    "惊讶": "surprise",
    "吃惊": "surprise",
    "sexy": "sexy",
    "性感": "sexy",
    "pain": "pain",
    "痛": "pain",
    "疼": "pain",
    "fear": "fear",
    "害怕": "fear",
    "fear2": "fear2",
    "silly": "silly",
    "搞怪": "silly",
    "worried": "worried",
    "担心": "worried",
    "embarrassed": "embarrassed",
    "害羞": "embarrassed",
    "尴尬": "embarrassed",
}

# Display names as they appear on the Person morph UI.
# Several ids are listed for the same look so an older package still matches.
RECIPES: dict[str, list[tuple[str, float]]] = {
    "neutral": [],
    "ahegao": [
        ("Eye Roll Back_DD", 0.22),
        ("Eye Rollback_DD", 0.22),
        ("CTRLEyesClosed", 0.0),
        ("CTRLEyeLidsBottomUp", 0.0),
        ("AA - Tongue 1", 0.45),
    ],
    "eyeroll": [
        ("Eye Roll Back_DD", 0.22),
        ("Eye Rollback_DD", 0.22),
        ("CTRLEyesClosed", 0.0),
        ("CTRLEyeLidsBottomUp", 0.0),
    ],
    "tongue": [
        ("AA - Tongue 1", 0.45),
    ],
    "smile": [("AA - Smile 1", 1.0)],
    "smile2": [("AA - Smile 2", 1.0)],
    "kiss": [("AA - Kiss 1", 1.0)],
    "kiss2": [("AA - Kiss 2", 1.0)],
    "kiss3": [("AA - Kiss 3", 1.0)],
    "pleasure": [
        ("06-Extreme Pleasure", 1.0),
        ("01-Extreme Pleasure", 0.85),
    ],
    "angry": [("AA - Anger 1", 1.0)],
    "sad": [("AA - Sad 1", 1.0)],
    "sad2": [("AA - Sad 2", 1.0)],
    "surprise": [("AA - Surprise 1", 1.0)],
    "sexy": [("AA - Sexy 1", 1.0)],
    "pain": [("AA - Pain 1", 1.0)],
    "fear": [("AA - Fear 1", 1.0)],
    "fear2": [("AA - Fear 2", 1.0)],
    "silly": [("AA - Silly 1", 1.0)],
    "worried": [("AA - Worry 1", 1.0)],
    "embarrassed": [("Embarassed1", 1.0)],
}

# Used by the vap fallback so leftover expression morphs are zeroed.
_RESET_NAMES: tuple[str, ...] = (
    "Eye Roll Back_DD",
    "Eye Rollback_DD",
    "01-Eyes Rolling",
    "02-Eyes Rolling",
    "08-Eyes Rolling",
    "01-Extreme Pleasure",
    "06-Extreme Pleasure",
    "AA - Tongue 1",
    "AA - Smile 1",
    "AA - Smile 2",
    "AA - Kiss 1",
    "AA - Kiss 2",
    "AA - Kiss 3",
    "AA - Anger 1",
    "AA - Anger 2",
    "AA - Sad 1",
    "AA - Sad 2",
    "AA - Surprise 1",
    "AA - Sexy 1",
    "AA - Sexy 2",
    "AA - Pain 1",
    "AA - Fear 1",
    "AA - Fear 2",
    "AA - Silly 1",
    "AA - Silly 2",
    "AA - Silly 3",
    "AA - Worry 1",
    "AA - Worry 2",
    "AA - Annoyed 1",
    "Embarassed1",
    "Embarassed2",
    "Enjoying It",
    "Taking It",
    "Mouth Resting",
    "Pouty",
)


def normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def resolve_recipe(name: str, strength: float) -> tuple[str, list[dict[str, Any]]]:
    raw = name.strip()
    if not raw:
        raise ValueError("empty expression name")
    key = normalize_name(raw)
    recipe_id = ALIASES.get(key) or ALIASES.get(raw)
    if recipe_id is None and key in RECIPES:
        recipe_id = key
    if recipe_id is not None:
        pairs = RECIPES[recipe_id]
        morphs = [{"name": morph, "value": round(val * strength, 4)} for morph, val in pairs]
        return recipe_id, morphs
    return raw, [{"name": raw, "value": strength}]


def list_aliases() -> list[dict[str, Any]]:
    by_id: dict[str, list[str]] = {}
    for alias, recipe_id in ALIASES.items():
        by_id.setdefault(recipe_id, [])
        if alias != recipe_id:
            by_id[recipe_id].append(alias)
    rows: list[dict[str, Any]] = []
    for recipe_id, pairs in RECIPES.items():
        rows.append(
            {
                "id": recipe_id,
                "aliases": by_id.get(recipe_id, []),
                "morphs": [name for name, _ in pairs],
            }
        )
    return rows


def list_expressions(query: str = "", person: str = "") -> dict[str, Any]:
    q = normalize_name(query)
    aliases = list_aliases()
    if q:
        aliases = [
            row
            for row in aliases
            if q in row["id"]
            or any(q in normalize_name(a) for a in row["aliases"])
            or any(q in normalize_name(m) for m in row["morphs"])
        ]
    payload: dict[str, Any] = {
        "aliases": aliases,
        "hint": (
            "Use set_expression with an alias (ahegao, eyeroll, tongue, smile, kiss, "
            "pleasure, angry, sad, surprise, sexy, pain, fear, silly, worried, "
            "embarrassed, neutral) or a morph name from items."
        ),
    }
    args: dict[str, Any] = {}
    if person:
        args["person"] = person
    try:
        live = bridge.call("list_expressions", timeout=15.0, **args)
        items = (live.get("data") or {}).get("items") or []
        if q:
            items = [
                item
                for item in items
                if q in normalize_name(str(item.get("name") or ""))
                or q in normalize_name(str(item.get("region") or ""))
            ]
        payload["person"] = (live.get("data") or {}).get("person")
        payload["count"] = len(items)
        payload["items"] = items
    except bridge.BridgeError as exc:
        payload["items"] = []
        payload["count"] = 0
        payload["liveError"] = str(exc)
        if "unknown op" in str(exc).lower():
            payload["reloadHint"] = (
                "Reload VamMcpBridge in Session Plugins to list live morphs. "
                "Aliases still work after reload, or via the vap fallback."
            )
    return payload


def _clamp_strength(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 2:
        return 2.0
    return float(value)


def _fallback_vap(person: str, expression: str, morphs: list[dict[str, Any]], reset: bool) -> dict[str, Any]:
    values: dict[str, float] = {}
    if reset:
        for name in _RESET_NAMES:
            values[name] = 0.0
    for row in morphs:
        values[str(row["name"])] = float(row["value"])
    preset = {
        "setUnlistedParamsToDefault": "false",
        "storables": [
            {
                "id": "geometry",
                "morphs": [
                    {"uid": name, "name": name, "value": str(val)}
                    for name, val in values.items()
                ],
            }
        ],
    }
    dest = vam_root() / "Custom" / "Atom" / "Person" / "Pose" / "Preset_VamMcp_Expression.vap"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(preset, ensure_ascii=False), encoding="utf-8")
    rel = dest.relative_to(vam_root()).as_posix()
    args: dict[str, Any] = {"path": rel}
    if person:
        args["person"] = person
    result = bridge.call("load_pose", timeout=45.0, **args)
    data = result.get("data") or result
    if not isinstance(data, dict):
        data = {"data": data}
    data["expression"] = expression
    data["kind"] = "expression"
    data["fallback"] = "vap"
    data["applied"] = morphs
    data["path"] = rel
    return data


def set_expression(
    name: str,
    person: str = "",
    value: float = 1.0,
    reset: bool = True,
) -> dict[str, Any]:
    strength = _clamp_strength(value)
    expression, morphs = resolve_recipe(name, strength)
    args: dict[str, Any] = {
        "expression": expression,
        "reset": reset,
        "morphs": morphs,
    }
    if person:
        args["person"] = person
    try:
        result = bridge.call("set_expression", timeout=20.0, **args)
        data = result.get("data") or result
        if not isinstance(data, dict):
            data = {"data": data}
        data["expression"] = expression
        return data
    except bridge.BridgeError as exc:
        if "unknown op" not in str(exc).lower():
            raise
        data = _fallback_vap(person, expression, morphs, reset)
        data["reloadHint"] = (
            "VamMcpBridge is older than 0.5.0. Applied via a keep-flag pose vap. "
            "Reload the Session Plugin to use live morph set_expression."
        )
        return data
