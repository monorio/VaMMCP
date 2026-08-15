from __future__ import annotations

import os
from pathlib import Path


def vam_root() -> Path:
    raw = os.environ.get("VAM_ROOT", "").strip().strip('"')
    if not raw:
        raise RuntimeError(
            "VAM_ROOT is not set. Point it at the folder that contains VaM.exe, "
            "for example VAM_ROOT=E:\\VaMX"
        )
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError(f"VAM_ROOT is not a directory: {root}")
    exe = root / "VaM.exe"
    if not exe.is_file():
        raise RuntimeError(f"VaM.exe not found under VAM_ROOT: {root}")
    return root


def bridge_dir(root: Path | None = None) -> Path:
    base = root or vam_root()
    path = base / "Saves" / "PluginData" / "vam-mcp"
    path.mkdir(parents=True, exist_ok=True)
    return path
