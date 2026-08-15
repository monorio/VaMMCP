from __future__ import annotations

import json
from typing import Any

from mcp.server import MCPServer

from . import __version__
from . import bridge
from .catalog import list_items

mcp = MCPServer(
    name="vam-mcp",
    version=__version__,
    instructions=(
        "Unofficial Virt-A-Mate controller. You can only load scenes, looks, and "
        "clothing that already exist on the user's machine. Search first, then load "
        "using the exact path returned by list_* tools. VAM must be running with "
        "the VamMcpBridge session plugin loaded."
    ),
)


def _dump(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def status() -> str:
    """Check VAM_ROOT and whether the VamMcpBridge session plugin is alive."""
    try:
        return _dump(bridge.status())
    except Exception as exc:
        return _dump({"ok": False, "error": str(exc)})


@mcp.tool()
def list_scenes(query: str = "", limit: int = 25) -> str:
    """Search local VAM scenes (Saves/scene and .var packages)."""
    items = list_items("scene", query=query, limit=limit)
    return _dump(
        {
            "count": len(items),
            "items": [item.__dict__ for item in items],
        }
    )


@mcp.tool()
def list_looks(query: str = "", limit: int = 25) -> str:
    """Search local appearance / look presets (.vap)."""
    items = list_items("look", query=query, limit=limit)
    return _dump(
        {
            "count": len(items),
            "items": [item.__dict__ for item in items],
        }
    )


@mcp.tool()
def list_clothing(query: str = "", limit: int = 25) -> str:
    """Search local clothing presets (.vap)."""
    items = list_items("clothing", query=query, limit=limit)
    return _dump(
        {
            "count": len(items),
            "items": [item.__dict__ for item in items],
        }
    )


@mcp.tool()
def list_persons() -> str:
    """List Person atoms in the currently loaded VAM scene."""
    result = bridge.call("list_persons", timeout=10.0)
    return _dump(result.get("data") or [])


@mcp.tool()
def load_scene(path: str, merge: bool = False) -> str:
    """Load a scene by the exact path from list_scenes. merge=True keeps the current scene and adds into it."""
    result = bridge.call("load_scene", timeout=90.0, path=path, merge=merge)
    return _dump(result.get("data") or result)


@mcp.tool()
def load_look(path: str, person: str = "") -> str:
    """Load an appearance/look preset onto a Person. person is the atom uid from list_persons; empty uses the first Person."""
    if path.lower().endswith(".json"):
        return _dump(
            {
                "ok": False,
                "error": (
                    "That path is a scene file, not an appearance preset. "
                    "Call load_scene with the same path (or merge=true to add it into the current scene)."
                ),
                "path": path,
            }
        )
    args: dict[str, Any] = {"path": path}
    if person:
        args["person"] = person
    result = bridge.call("load_look", timeout=45.0, **args)
    return _dump(result.get("data") or result)


@mcp.tool()
def load_clothing(path: str, person: str = "") -> str:
    """Load a clothing preset onto a Person. person is the atom uid from list_persons; empty uses the first Person."""
    args: dict[str, Any] = {"path": path}
    if person:
        args["person"] = person
    result = bridge.call("load_clothing", timeout=45.0, **args)
    return _dump(result.get("data") or result)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
