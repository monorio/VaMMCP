from __future__ import annotations

import json
import re
import time
import zipfile
from pathlib import Path
from typing import Any

from . import bridge
from .catalog import list_items
from .paths import vam_root

# vamX paired sex poses. Keys are pose kind + environment hint.
COUPLE_POSES = {
    "doggy": {
        "secret room": (
            "vamX.1.52:/Custom/Atom/Person/Pose/Preset_ROOT_F_Standing_Doggie_Secret Room Bed.vap",
            "vamX.1.52:/Custom/Atom/Person/Pose/Preset_ROOT_M_Standing_Doggie_Secret Room Bed.vap",
        ),
        "default": (
            "vamX.1.52:/Custom/Atom/Person/Pose/Preset_F_Missionary_Doggie.vap",
            "vamX.1.52:/Custom/Atom/Person/Pose/Preset_M_Missionary_Doggie.vap",
        ),
    },
    "missionary": {
        "default": (
            "vamX.1.52:/Custom/Atom/Person/Pose/Preset_F_Missionary_Doggie.vap",
            "vamX.1.52:/Custom/Atom/Person/Pose/Preset_M_Missionary_Doggie.vap",
        ),
    },
}

POSE_KIND_ALIASES = {
    "doggy": "doggy",
    "doggie": "doggy",
    "后入": "doggy",
    "后入式": "doggy",
    "从后面": "doggy",
    "missionary": "missionary",
    "传教士": "missionary",
    "正入": "missionary",
}


def normalize_pose_kind(text: str) -> str:
    key = (text or "").strip().lower()
    return POSE_KIND_ALIASES.get(key, key or "doggy")


def detect_environment(scene_info: dict[str, Any]) -> str:
    blob = " ".join(
        str(x) for x in (scene_info.get("atomTypes") or []) + (scene_info.get("atomNames") or [])
    ).lower()
    if "secret" in blob or "macgruber" in blob:
        return "secret room"
    if "apartment" in blob or "cyberpunk" in blob:
        return "default"
    return "default"


def resolve_look(query: str) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {"ok": False, "error": "empty look query"}
    if q.lower().endswith(".vap"):
        return {"ok": True, "path": q, "source": "path"}
    items = list_items("look", query=q, limit=20)
    vap = [i for i in items if i.path.lower().endswith(".vap")]
    chosen = vap[0] if vap else (items[0] if items else None)
    if chosen is None:
        return {"ok": False, "error": "no local look matched: " + q}
    if chosen.path.lower().endswith(".vap"):
        return {"ok": True, "path": chosen.path, "name": chosen.name, "source": chosen.source}
    extracted = extract_scene_look(chosen.path, chosen.name)
    if not extracted.get("ok"):
        return extracted
    extracted["name"] = chosen.name
    return extracted


def extract_scene_look(scene_path: str, name: str) -> dict[str, Any]:
    root = vam_root()
    data = None
    if ":/" in scene_path:
        package, inner = scene_path.split(":/", 1)
        var_file = None
        for cand in (root / "AddonPackages").rglob(package + ".var"):
            var_file = cand
            break
        if var_file is None:
            return {"ok": False, "error": "package not found: " + package}
        with zipfile.ZipFile(var_file) as zf:
            data = json.loads(zf.read(inner.replace("\\", "/")))
    else:
        data = json.loads((root / scene_path).read_text(encoding="utf-8"))
    person = None
    for atom in data.get("atoms") or []:
        if atom.get("type") == "Person":
            person = atom
            break
    if person is None:
        return {"ok": False, "error": "no Person in look scene: " + scene_path}
    dest_dir = root / "Custom" / "Atom" / "Person" / "Appearance"
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name)[:60]
    dest = dest_dir / ("Preset_VamMcp_" + slug + ".vap")
    vap = {
        "setUnlistedParamsToDefault": "true",
        "storables": person.get("storables") or [],
    }
    dest.write_text(json.dumps(vap, ensure_ascii=False), encoding="utf-8")
    rel = dest.relative_to(root).as_posix()
    return {"ok": True, "path": rel, "extractedFrom": scene_path}


def pick_couple_paths(kind: str, environment: str) -> tuple[str, str]:
    table = COUPLE_POSES.get(kind) or COUPLE_POSES["doggy"]
    return table.get(environment) or table.get("default") or COUPLE_POSES["doggy"]["default"]


def setup_couple(female: str, male: str = "", pose: str = "doggy") -> dict[str, Any]:
    kind = normalize_pose_kind(pose)
    female_look = resolve_look(female)
    if not female_look.get("ok"):
        return female_look
    male_look = None
    if male.strip():
        male_look = resolve_look(male)
        if not male_look.get("ok"):
            return male_look

    try:
        info = bridge.call("scene_info", timeout=10.0).get("data") or {}
    except Exception:
        info = {"persons": bridge.call("list_persons", timeout=10.0).get("data") or []}

    persons = info.get("persons") or []
    env = detect_environment(info)
    female_uid, male_uid, notes = _assign_people(persons)

    steps: list[Any] = []
    if female_uid:
        try:
            bridge.call("set_person_on", timeout=10.0, person=female_uid, on=True)
            steps.append({"set_on": female_uid})
        except Exception as exc:
            notes.append("could not enable " + female_uid + ": " + str(exc))
        steps.append(bridge.call("load_look", timeout=45.0, path=female_look["path"], person=female_uid))
    if male_uid and male_look:
        try:
            bridge.call("set_person_on", timeout=10.0, person=male_uid, on=True)
            steps.append({"set_on": male_uid})
        except Exception as exc:
            notes.append("could not enable " + male_uid + ": " + str(exc))
        steps.append(bridge.call("load_look", timeout=45.0, path=male_look["path"], person=male_uid))

    f_pose, m_pose = pick_couple_paths(kind, env)
    if female_uid:
        steps.append(bridge.call("load_pose", timeout=45.0, path=f_pose, person=female_uid))
    if male_uid:
        steps.append(bridge.call("load_pose", timeout=45.0, path=m_pose, person=male_uid))

    return {
        "ok": True,
        "pose": kind,
        "environment": env,
        "female": {"uid": female_uid, "look": female_look},
        "male": {"uid": male_uid, "look": male_look},
        "poses": {"female": f_pose, "male": m_pose},
        "notes": notes,
    }


def _assign_people(persons: list[Any]) -> tuple[str, str, list[str]]:
    notes: list[str] = []
    female_uid = ""
    male_uid = ""
    for row in persons:
        gender = str(row.get("gender") or "")
        uid = str(row.get("uid") or "")
        if gender == "female" and not female_uid:
            female_uid = uid
        elif gender == "male" and uid != "AsianMale" and not male_uid:
            male_uid = uid
    if not female_uid:
        for row in persons:
            uid = str(row.get("uid") or "")
            if uid == "Person":
                female_uid = uid
                break
        if not female_uid and persons:
            female_uid = str(persons[0].get("uid") or "")
    if not male_uid:
        for row in persons:
            uid = str(row.get("uid") or "")
            if uid in {"Person#2", "MCPPerson"} or uid.lower().endswith("male"):
                if uid != female_uid:
                    male_uid = uid
                    break
    if not male_uid:
        try:
            bridge.call("add_person", timeout=20.0, uid="MCPPerson")
            time.sleep(2.0)
            male_uid = "MCPPerson"
            notes.append("added MCPPerson")
        except Exception as exc:
            notes.append("could not add male: " + str(exc))
    return female_uid, male_uid, notes
