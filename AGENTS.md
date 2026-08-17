# AGENTS.md

If you are an agent (Codex, Claude Code, Cursor, Grok, Copilot, Cline, …), **read this file first and follow it**.

你是 Agent 时：**先读本文件再动手**。

## What this repo is

Unofficial Virt-A-Mate controller: Python MCP server `vam-mcp` plus session plugin `VamMcpBridge`.

It **only** searches and loads files already on the user's disk (scenes, looks, clothing, poses, face morphs). It does **not** generate characters, clothes, or Hub downloads.

## VAM_ROOT (required)

`VAM_ROOT` is the folder that contains `VaM.exe`.

- If the user has not given this path, **ask for it**. Do not guess a drive letter or a default install folder.
- Confirm `VaM.exe` exists in that folder before copying files there.

## Install steps the agent should run

When the plugin is not in `AddonPackages` yet, or the user asks to install:

1. Ask for `VAM_ROOT` if you do not have it.
2. From this repo root, pack the plugin:

   ```powershell
   .\scripts\pack-var.ps1 -Version 1
   ```

   This writes `dist-var\VamMcp.Bridge.1.var`.
3. Copy that file into the VAM install:

   ```
   VAM_ROOT\AddonPackages\VamMcp.Bridge.1.var
   ```

4. Stop. Tell the user they must, in VAM:
   - User Preferences -> Security -> Enable Plugins
   - restart VAM if it was already running (so it rescans packages)
   - Session Plugins -> Add Plugin -> `VamMcp.Bridge` -> `VamMcpBridge.cs`
   - leave `enabled` on
   - Session Plugin Presets -> Change User Defaults -> Set Current As User Defaults
5. Do **not** click the VAM UI yourself. Do **not** kill `VaM.exe` unless the user asks.

Optional, if the MCP server is not installed yet (from repo `mcp\`):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Then point the current MCP client at that venv Python with env `VAM_ROOT` set to the path the user gave.

## Preconditions (before any scene work)

1. Virt-A-Mate / VaMX is running.
2. `VamMcpBridge` is loaded under **Session Plugins** (not Scene Plugins, not on a Person) and `enabled` is on.
3. MCP server `vam` is connected (`VAM_ROOT` = folder that contains `VaM.exe`).
4. Call `status` first. If the plugin is missing or the call times out: run the install file steps above if needed, then tell the user to finish the Session Plugin clicks. Do not invent clicks in the VAM UI.

## Operating rules

- Prefer MCP tools on the `vam` server. Do not ask the user to click **On**, delete atoms, or browse presets by hand when a tool exists.
- Looks / poses / scenes must already exist. If `list_*` returns nothing, say so. Do not promise to create or download content.
- Workflow: `list_*` -> pick an exact `path` (or uid) -> `load_*`.
- After any scene, look, clothing, pose, or expression change, call `capture_view` and inspect `Saves/PluginData/vam-mcp/preview.png` (the tool returns `previewAbsolute`).
- Face only: `set_expression` (alias or a morph name from `list_expressions`). Neutral aliases include `smile`, `neutral`, `surprise`, `sad`, `angry`.
- Head tracking the monitor camera: `lock_head`.
- Two people into the current room with a paired pose: `setup_couple(female, male, pose)`. `female` / `male` are look names or exact `.vap` paths. `pose` is whatever the user asked for (or a name from `list_poses`). If the paired pose package is missing, fall back to `list_poses` + `load_pose` per person.
- Hidden people: `set_person_on`. Extra person: `add_person`, then `load_look` / `load_pose` on the returned uid. Remove: `remove_person`.
- `load_look` rejects `.json` scene files — those go to `load_scene` (use `merge=true` to add into the current scene).
- `person=""` = first Person. `person="all"` on `load_pose` applies the pose to everyone.
- After the user adds new `.var` / look files, the catalog is stale until the MCP process restarts. Say that; do not claim the new files are visible.

## Tools

| Tool | Use |
| --- | --- |
| `status` | Bridge alive? Call first. |
| `list_scenes` / `load_scene` | Search / load a scene |
| `list_persons` | Person atoms in the current scene |
| `add_person` / `remove_person` / `set_person_on` | Add, delete, show/hide |
| `capture_view` | Screenshot to `preview.png` |
| `list_looks` / `load_look` | Appearance `.vap` |
| `list_clothing` / `load_clothing` | Clothing `.vap` |
| `list_poses` / `load_pose` | Pose `.vap` |
| `list_expressions` / `set_expression` | Face aliases and live morphs |
| `lock_head` | Stop the head following the camera |
| `setup_couple` | Two looks + paired pose in the current scene |

## If MCP is not connected

Install the Python package as above and attach `vam-mcp` to this agent. `VAM_ROOT` must be the folder the user named (the one with `VaM.exe`). Do not drive VAM by editing Unity files or sending raw JSON unless they explicitly ask you to debug the file bridge.

## Safety

Treat this as full control of the running VAM session. Only load paths the user asked for. Do not expose `Saves/PluginData/vam-mcp`.
