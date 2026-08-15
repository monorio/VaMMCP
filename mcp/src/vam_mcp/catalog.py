from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

from .paths import vam_root


@dataclass(frozen=True)
class CatalogItem:
    kind: str
    name: str
    path: str
    source: str


_CACHE: dict[str, list[CatalogItem]] | None = None


def list_items(kind: str, query: str = "", limit: int = 25) -> list[CatalogItem]:
    if kind not in {"scene", "look", "clothing"}:
        raise ValueError(f"unknown kind: {kind}")
    q = query.strip().lower()
    items = _cached_scan(kind)
    if q:
        items = [item for item in items if q in item.name.lower() or q in item.path.lower()]
    items.sort(key=lambda item: (item.name.lower(), item.path.lower()))
    return items[: max(1, min(limit, 100))]


def _cached_scan(kind: str) -> list[CatalogItem]:
    global _CACHE
    if _CACHE is None:
        _CACHE = {
            "scene": _scan("scene"),
            "look": _scan("look"),
            "clothing": _scan("clothing"),
        }
    return _CACHE[kind]


def _scan(kind: str) -> list[CatalogItem]:
    root = vam_root()
    found: dict[str, CatalogItem] = {}

    for item in _scan_loose(root, kind):
        found[item.path] = item

    addon = root / "AddonPackages"
    if addon.is_dir():
        for var_path in addon.rglob("*.var"):
            try:
                for item in _scan_var(var_path, kind):
                    found.setdefault(item.path, item)
            except (OSError, zipfile.BadZipFile):
                continue

    return list(found.values())


def _scan_loose(root: Path, kind: str) -> list[CatalogItem]:
    items: list[CatalogItem] = []
    if kind == "scene":
        roots = [root / "Saves" / "scene"]
        suffix = ".json"
    elif kind == "look":
        roots = [
            root / "Custom" / "Atom" / "Person" / "Appearance",
            root / "Saves" / "Person" / "appearance",
        ]
        suffix = ".vap"
    else:
        roots = [root / "Custom" / "Atom" / "Person" / "Clothing"]
        suffix = ".vap"

    for base in roots:
        if not base.is_dir():
            continue
        for file_path in base.rglob(f"*{suffix}"):
            if not file_path.is_file():
                continue
            if kind == "scene" and file_path.name.lower().endswith(".json.jpg"):
                continue
            rel = file_path.relative_to(root).as_posix()
            items.append(
                CatalogItem(
                    kind=kind,
                    name=file_path.stem,
                    path=rel,
                    source="loose",
                )
            )
    return items


def _scan_var(var_path: Path, kind: str) -> list[CatalogItem]:
    package_ref = var_path.stem
    items: list[CatalogItem] = []
    with zipfile.ZipFile(var_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            inner = info.filename.replace("\\", "/")
            if not _matches_kind(kind, inner, package_ref):
                continue
            name = Path(inner).stem
            items.append(
                CatalogItem(
                    kind=kind,
                    name=name,
                    path=f"{package_ref}:/{inner}",
                    source=var_path.name,
                )
            )
    return items


def _matches_kind(kind: str, inner: str, package_ref: str = "") -> bool:
    lower = "/" + inner.lower().lstrip("/")
    package = package_ref.lower()
    if kind == "scene":
        return lower.endswith(".json") and "/saves/scene/" in lower
    if kind == "look":
        if lower.endswith(".vap") and (
            "/appearance/" in lower or "/look/" in lower or "/looks/" in lower
        ):
            return True
        # Many Hub looks are a single scene JSON inside a *Look* package.
        if lower.endswith(".json") and "/saves/scene/" in lower:
            return "look" in package or "look" in lower
        return False
    return lower.endswith(".vap") and "/clothing/" in lower
