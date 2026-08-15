# VamMCP

Unofficial [Model Context Protocol](https://modelcontextprotocol.io/) server plus a Virt-A-Mate **session plugin**. Talk to an MCP client and load scenes, looks, and clothing that already exist in your local VAM library.

This project is **not affiliated with Mesh VR or Virt-A-Mate**. You must own a legal copy of VAM or VaMX. Adults only (18+). See [NOTICE.md](NOTICE.md).

**It does not generate characters or clothes.** It only searches and loads files already on disk.

## How it works

```
MCP client  →  vam-mcp (Python)  →  Saves/PluginData/vam-mcp/*.json  →  VamMcpBridge (session plugin)  →  SuperController
```

The first version uses a local file bridge so it does not depend on HTTP inside Unity.

## Requirements

- Windows
- Virt-A-Mate 1.20+ or VaMX with `VaM.exe`
- Python 3.10+ ([uv](https://github.com/astral-sh/uv) recommended)
- An MCP client (Grok, Claude Desktop, Cursor, …)

## Install

### 1. Plugin

**Release build:** copy `VamMcp.Bridge.N.var` from [Releases](../../releases) into `AddonPackages`.

**Development:** from a clone of this repo:

```powershell
.\scripts\install-dev.ps1 -VamRoot "C:\Path\To\Your\VAM"
```

Then in VAM:

1. Main UI → **Session Plugins** → Add Plugin → `Custom/Scripts/VamMcp/Bridge/VamMcpBridge.cs`
2. Session Plugin Presets → set current as user default (so the bridge survives restarts)
3. Leave VAM running

Scene plugins are destroyed on scene load. This one must stay on **Session Plugins**.

### 2. MCP server

```powershell
cd mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Point the client at the server and set `VAM_ROOT` to the folder that contains `VaM.exe`. See [examples/claude_desktop.json](examples/claude_desktop.json) and [examples/grok.mcp.json](examples/grok.mcp.json).

```json
{
  "mcpServers": {
    "vam": {
      "command": "C:\\Path\\To\\VamMCP\\mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "vam_mcp.server"],
      "env": { "VAM_ROOT": "C:\\Path\\To\\Your\\VAM" }
    }
  }
}
```

With [uv](https://github.com/astral-sh/uv) you can use `uv --directory ... run vam-mcp` instead of the venv python.

### 3. Smoke test

With VAM running and the plugin loaded:

```powershell
.\scripts\ping-bridge.ps1 -VamRoot "C:\Path\To\Your\VAM"
```

## Tools

| Tool | Role |
| --- | --- |
| `status` | Is the plugin alive? |
| `list_scenes` / `load_scene` | Search and load a scene |
| `list_persons` | Person atoms in the current scene |
| `list_looks` / `load_look` | Search and apply an appearance preset |
| `list_clothing` / `load_clothing` | Search and apply a clothing preset |

Typical chat flow: search (`list_*`) → pick an exact `path` → `load_*`.

## Pack a .var for GitHub Releases

```powershell
.\scripts\pack-var.ps1 -Version 1
```

Commit source only. Attach `dist-var/VamMcp.Bridge.1.var` to the GitHub Release. Do not commit `.var` files, looks, scenes, or a VAM install.

Before the first public push, change `creatorName` / repo URLs in `plugin/meta.json` to your GitHub account.

## Safety

- Local files only. Nothing is served on the network.
- The tools can load any scene or preset visible under `VAM_ROOT`. That is full control of the running session.
- Do not attach this MCP server to untrusted agents or expose `Saves/PluginData/vam-mcp`.

## License

[MIT](LICENSE) for the code in this repository. Virt-A-Mate remains under its own EULA.
