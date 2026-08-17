# VamMCP

[English](#vammcp) | [中文](#中文)

> **Agents (Codex, Claude Code, Cursor, Grok, Copilot, …):** read **[AGENTS.md](AGENTS.md)** first and follow it. Do not improvise a VAM workflow from this README.

Unofficial [Model Context Protocol](https://modelcontextprotocol.io/) server plus a Virt-A-Mate **session plugin**. Talk to an MCP-capable agent and load scenes, looks, clothing, poses, and expressions that already exist in your local VAM library.

This project is **not affiliated with Mesh VR or Virt-A-Mate**. You must own a legal copy of VAM or VaMX. See [NOTICE.md](NOTICE.md).

**It does not generate characters or clothes.** It only searches and loads files already on disk.

Current pieces:

| Piece | Version |
| --- | --- |
| Session plugin `VamMcpBridge` | 0.5.1 |
| Python package `vam-mcp` | 0.2.0 |

## How it works

```
MCP client  →  vam-mcp (Python)  →  Saves/PluginData/vam-mcp/*.json  →  VamMcpBridge (session plugin)  →  SuperController
```

The bridge is a pair of local JSON files. Nothing is served on the network, and nothing talks HTTP inside Unity.

## What you need

- Windows
- Virt-A-Mate **1.20+** or VaMX whose install folder contains `VaM.exe`
- Python **3.10+** ([uv](https://github.com/astral-sh/uv) is optional)
- An MCP client / coding agent (Codex, Claude Code, Cursor, Grok, Copilot, …)
- Looks / scenes / clothing / poses already in that VAM install

`setup_couple` extra: a local package that still has paired F/M pose files (the server currently looks under `vamX.1.52:/Custom/Atom/Person/Pose/...`). Face aliases need the matching morphs on the Person. If those files are missing, the tool reports `missing` instead of inventing a face.

## Install (do these in order)

You need **both** halves: the VAM plugin and the Python MCP server. The plugin must be a **Session Plugin**, not a Scene Plugin and not a plugin on a Person atom.

### 1. Allow plugins in VAM

1. Start VAM / VaMX.
2. Open the main UI (`Esc`).
3. **User Preferences → Security**.
4. Turn **Enable Plugins** on.
5. Recommended: turn **Plugins Always Enabled** on so VAM does not ask “allow this plugin?” every launch.

If you skip this, `Add Plugin` will either be missing or the script will sit there unused.

### 2. Install the VamMcpBridge plugin

#### Option A — `.var` package (normal use)

1. Get `VamMcp.Bridge.N.var`:
   - from [Releases](../../releases), or
   - build one yourself with `.\scripts\pack-var.ps1 -Version 1` (writes `dist-var\VamMcp.Bridge.1.var`).
2. Copy that file into the **`AddonPackages`** folder next to `VaM.exe`.

   ```
   <VAM_ROOT>\AddonPackages\VamMcp.Bridge.1.var
   ```

3. If VAM was already running, **restart it** so it rescans packages.

#### Option B — development copy from this repo

From a clone of this repository:

```powershell
.\scripts\install-dev.ps1 -VamRoot "C:\Path\To\Your\VAM"
```

That junctions (or copies) `plugin\` to:

```
<VAM_ROOT>\Custom\Scripts\VamMcp\Bridge\VamMcpBridge.cs
```

After you edit the `.cs` file, open **Session Plugins** and click **Reload** on `VamMcpBridge`. A VAM restart is not required.

### 3. Enable the plugin in the game

Scene plugins are destroyed when a scene loads. This one **must** stay on **Session Plugins**.

1. Start VAM and open the main UI (`Esc`).
2. Open the purple **Session Plugins** tab (main menu, not a Person atom).
3. Click **Add Plugin**.
4. In the file browser pick `VamMcpBridge.cs`:
   - from a `.var`: package **`VamMcp.Bridge`** → `Custom/Scripts/VamMcp/Bridge/VamMcpBridge.cs`
   - from a dev install: `Custom/Scripts/VamMcp/Bridge/VamMcpBridge.cs`
5. If VAM asks to allow the plugin, choose **Allow**.
6. Confirm the plugin row is present and:
   - the **`enabled`** toggle is on
   - the status text says something like `ready  root=...`
7. Keep it across restarts:
   - still on the Session Plugins panel, open **Session Plugin Presets**
   - **Change User Defaults → Set Current As User Defaults**

   If you skip it, the bridge is gone the next time you launch VAM.

Leave VAM running. The MCP server only works while this plugin is loaded and `enabled`.

### 4. Install the Python MCP server

```powershell
cd C:\Path\To\VamMCP\mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

`VAM_ROOT` must be the folder that contains `VaM.exe`, for example `C:\VaM` or `E:\VaMX`.

With [uv](https://github.com/astral-sh/uv) you can skip the venv and run `uv --directory C:\Path\To\VamMCP\mcp run vam-mcp` instead.

### 5. Configure the agent / MCP client

Replace the two paths. `command` is this repo’s venv Python; `VAM_ROOT` is the VAM/VaMX install. After saving, restart the agent or reload its MCP list.

Open **this repository** as the workspace so the agent auto-loads [AGENTS.md](AGENTS.md).

#### Codex (CLI / IDE)

Append [examples/codex.config.toml](examples/codex.config.toml) to `%USERPROFILE%\.codex\config.toml` (or a project `.codex\config.toml`):

```toml
[mcp_servers.vam]
command = 'C:\Path\To\VamMCP\mcp\.venv\Scripts\python.exe'
args = ["-m", "vam_mcp.server"]

[mcp_servers.vam.env]
VAM_ROOT = 'C:\Path\To\Your\VAM'
```

Or:

```powershell
codex mcp add vam --env VAM_ROOT=C:\Path\To\Your\VAM -- C:\Path\To\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server
```

Then `cd` into this repo and start Codex. It reads `AGENTS.md` automatically.

#### Grok

Append [examples/grok.config.toml](examples/grok.config.toml) to `%USERPROFILE%\.grok\config.toml` (or a project `.grok\config.toml`):

```toml
[mcp_servers.vam]
command = 'C:\Path\To\VamMCP\mcp\.venv\Scripts\python.exe'
args = ["-m", "vam_mcp.server"]
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120

[mcp_servers.vam.env]
VAM_ROOT = 'C:\Path\To\Your\VAM'
```

Or `grok mcp add vam -e VAM_ROOT=C:\Path\To\Your\VAM -- C:\Path\To\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server`. In Grok run `/mcps` and press `r` to reload.

#### Claude Code

```powershell
claude mcp add vam --env VAM_ROOT=C:\Path\To\Your\VAM -- C:\Path\To\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server
```

Claude Code also reads `AGENTS.md` (and `CLAUDE.md` if you add one that points here). Open this repo as the project.

#### Cursor, Copilot, and other JSON clients

Same shape as [examples/claude_desktop.json](examples/claude_desktop.json) / [examples/grok.mcp.json](examples/grok.mcp.json):

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

| Client | Config file |
| --- | --- |
| Codex | `%USERPROFILE%\.codex\config.toml` |
| Grok | `%USERPROFILE%\.grok\config.toml` |
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `%USERPROFILE%\.cursor\mcp.json` or `<project>\.cursor\mcp.json` |
| VS Code Copilot | MCP section in user/workspace `mcp.json` |
| Any agent that reads `.mcp.json` | project root `.mcp.json` (same JSON as above) |

You should see a `vam` server with tools such as `status`, `list_scenes`, `setup_couple`.

### 6. Smoke test

With VAM running and `VamMcpBridge` loaded:

```powershell
.\scripts\ping-bridge.ps1 -VamRoot "C:\Path\To\Your\VAM"
```

A JSON payload with `"ok": "true"` and `"plugin": "VamMcpBridge"` means the file bridge works. Then ask the agent to call `status`.

## Daily use

1. Start **VAM first**, wait until the Session Plugin status says `ready`.
2. Start the agent **in this repo** so it sees [AGENTS.md](AGENTS.md).
3. Talk in plain language. The agent should call `list_*` then `load_*` (or `setup_couple` for two people plus a paired pose).

Examples:

- “What people are in the current scene?”
- “Search looks for this name and load that appearance.”
- “Add these two people to the current room and sit them down.”
- “Set her expression to smile.”
- “Her head is tracking the camera — lock the head.”

After any scene / look / pose change the server writes a screenshot to `Saves/PluginData/vam-mcp/preview.png`. Ask the agent to `capture_view` if you want to check the result.

Typical tool flow: `list_*` → pick an exact `path` → `load_*`. Face changes use `set_expression` (plugin **0.5.0+**). Head tracking uses `lock_head` (plugin **0.5.1+**). After you update `VamMcpBridge.cs`, **Reload** the Session Plugin.

## Tools

| Tool | Role |
| --- | --- |
| `status` | Is `VAM_ROOT` valid and is the plugin alive? |
| `list_scenes` / `load_scene` | Search and load a scene (`merge=true` adds into the current scene) |
| `list_persons` | Person atoms in the current scene |
| `add_person` / `remove_person` / `set_person_on` | Add, delete, or show/hide a Person |
| `capture_view` | Save the monitor camera to `Saves/PluginData/vam-mcp/preview.png` |
| `list_looks` / `load_look` | Search and apply an appearance preset |
| `list_clothing` / `load_clothing` | Search and apply a clothing preset |
| `list_poses` / `load_pose` | Search and apply a pose (`person=all` poses everyone) |
| `list_expressions` / `set_expression` | List aliases / live face morphs, then set a face (`smile`, `neutral`, `surprise`, …) |
| `lock_head` | Hold the head still so it does not follow the monitor camera |
| `setup_couple` | One-shot: resolve two looks, enable or add people, apply a paired pose |

Do not ask the user to click **On** or delete atoms by hand — `set_person_on` / `remove_person` do that.

## Known limits

- Scene catalog is cached for the life of the MCP process. After you drop new `.var` files or looks into VAM, restart the MCP server so `list_*` sees them.
- `setup_couple` paired-pose paths currently assume **vamX 1.52**. A different package version will fail those `load_pose` calls unless that exact package is still installed.
- `set_expression` only drives morphs that are already on the Person. Missing morphs show up in `missing`; the face will not change.
- `lock_head` holds head/neck controllers and sets eyes to Target. A glance / look-at plugin on the Person can still turn the head — disable that plugin or lock again after it loads.
- `add_person` starts a VAM coroutine and returns immediately. `setup_couple` waits about two seconds; a slow machine may need a retry.
- `list_*` / `load_*` never create Hub content. If the look is not on disk, the answer is “not found”.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `status` says plugin missing | VAM is not running, or the Session Plugin was never added / not set as user default |
| MCP tool times out | Plugin `enabled` toggle is off; VAM is on a loading screen; or the plugin is a Scene Plugin and a scene load destroyed it |
| `Add Plugin` does nothing | **User Preferences → Security → Enable Plugins** |
| Plugin vanishes after restart | Session Plugin Presets → **Set Current As User Defaults** |
| `VaM.exe not found` | `VAM_ROOT` is not the folder that contains `VaM.exe` |
| `unknown op: set_expression` / `lock_head` | Old plugin. Update the `.cs` / `.var` and **Reload** the Session Plugin (need 0.5.0+ / 0.5.1+) |
| New looks do not appear in `list_looks` | Restart the MCP server so it rescans `AddonPackages` |
| `setup_couple` pose fails | Use `list_poses` / `load_pose`, or install the paired-pose package the server expects |
| Ping script says no response | Same as timeout: VAM running, Session Plugin loaded, `enabled` on |
| Agent ignores VAM tools | Workspace is not this repo (so `AGENTS.md` was not loaded), or the `vam` MCP server is not connected |

## Pack a `.var` for GitHub Releases

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

---

## 中文

Agent (Codex / Claude Code / Cursor / Grok / Copilot) 请先读 [AGENTS.md](AGENTS.md)，再动手。

非官方 [MCP](https://modelcontextprotocol.io/) 服务 + Virt-A-Mate Session 插件。用对话加载本机已经有的场景、Look、服装、姿势和表情。

和 Mesh VR / Virt-A-Mate 没有隶属关系。需要自己拥有合法的 VAM 或 VaMX。详见 [NOTICE.md](NOTICE.md)。

不能生成角色或衣服，只能搜索并加载硬盘上已有的文件。

当前版本：Session 插件 `VamMcpBridge` 0.5.1，Python 包 `vam-mcp` 0.2.0。

### 原理

MCP 客户端 -> vam-mcp (Python) -> Saves/PluginData/vam-mcp 下的 JSON -> VamMcpBridge (Session 插件) -> SuperController

走本地文件桥，不在 VAM 里开 HTTP，也不监听网络端口。

### 环境

- Windows
- Virt-A-Mate 1.20+，或安装目录里有 VaM.exe 的 VaMX
- Python 3.10+
- 支持 MCP 的客户端：Codex、Claude Code、Cursor、Grok、Copilot 等
- 本机 VAM 里已经有场景 / Look / 服装 / 姿势

`setup_couple` 需要本机有成对的 F/M 姿势文件（目前查找 vamX.1.52 包里的 Pose）。表情别名需要角色身上已有对应 morph。缺文件时工具会列出 missing，不会凭空捏脸。

### 安装顺序

两边都要装：VAM 插件，以及 Python MCP 服务。插件必须加在 Session Plugins，不要加到 Scene Plugins，也不要加在某个 Person 身上。

#### 1. 先在 VAM 里允许插件

1. 启动 VAM / VaMX
2. 按 Esc 打开主界面
3. User Preferences -> Security
4. 打开 Enable Plugins
5. 建议同时打开 Plugins Always Enabled，避免每次启动都弹是否允许插件

这一步没开的话，后面 Add Plugin 会没有入口。

#### 2. 安装 VamMcpBridge 插件

日常安装用 var 包：

1. 从 [Releases](https://github.com/monorio/VaMMCP/releases) 下载 `VamMcp.Bridge.N.var`，或在本仓库执行 `scripts/pack-var.ps1 -Version 1`
2. 复制到 VaM.exe 旁边的 AddonPackages 目录，例如 `E:\VaMX\AddonPackages\VamMcp.Bridge.1.var`
3. 如果 VAM 当时是开着的，重启一次，让它重新扫描包

开发安装：

```powershell
.\scripts\install-dev.ps1 -VamRoot "E:\VaMX"
```

脚本会把 plugin 目录联接到 `Custom\Scripts\VamMcp\Bridge\VamMcpBridge.cs`。以后改了 cs 文件，在 Session Plugins 里对 VamMcpBridge 点 Reload 即可。

#### 3. 在游戏里启用插件

1. 启动 VAM，按 Esc
2. 打开主菜单上紫色的 Session Plugins（不要点到角色身上的 Plugins）
3. 点 Add Plugin
4. 选 VamMcpBridge.cs：var 安装走包名 VamMcp.Bridge；开发安装走 Custom/Scripts/VamMcp/Bridge
5. 如果弹出是否允许，选 Allow
6. 确认 enabled 开关是打开的，状态类似 ready
7. Session Plugin Presets -> Change User Defaults -> Set Current As User Defaults

不设默认的话，下次开 VAM 桥就没了。保持 VAM 开着，MCP 才能响应。

#### 4. 安装 Python MCP 服务

```powershell
cd E:\VamMCP\mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

VAM_ROOT 必须指向包含 VaM.exe 的目录，例如 E:\VaMX。

#### 5. 配置 Agent

command 是本仓库 venv 里的 python.exe，VAM_ROOT 是 VAM 安装目录。改完后重启 Agent。请把本仓库当作工作区打开，这样会自动加载 AGENTS.md。

Codex 写入 `%USERPROFILE%\.codex\config.toml`：

```toml
[mcp_servers.vam]
command = 'E:\VamMCP\mcp\.venv\Scripts\python.exe'
args = ["-m", "vam_mcp.server"]

[mcp_servers.vam.env]
VAM_ROOT = 'E:\VaMX'
```

也可以：

```powershell
codex mcp add vam --env VAM_ROOT=E:\VaMX -- E:\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server
```

Grok 写入 `%USERPROFILE%\.grok\config.toml`，或执行 `grok mcp add vam ...`。Claude Code 用 `claude mcp add vam ...`。Cursor / Copilot 用标准 mcp.json，示例见 examples 目录。

#### 6. 连通测试

VAM 已开、插件已加载时：

```powershell
.\scripts\ping-bridge.ps1 -VamRoot "E:\VaMX"
```

返回 ok 和 plugin 为 VamMcpBridge 就说明文件桥通了。然后再让 Agent 调用一次 status。

### 日常怎么用

1. 先开 VAM，等到 Session Plugin 状态变成 ready
2. 在本仓库里启动 Agent
3. 直接说话。Agent 应先 list 再 load；两个人加进当前房间并套成对姿势走 setup_couple

可以说：当前场景里有哪些人；搜这个名字的外观并加载；把这两个人加进当前房间并坐下；给她换成微笑；头跟着镜头转就锁住头。

变更后预览图在 `Saves/PluginData/vam-mcp/preview.png`。需要核对结果时让 Agent 再调 capture_view。

### 工具

- status：插件是否在线
- list_scenes / load_scene：搜或加载场景，merge=true 合并进当前场景
- list_persons：当前场景里的人物
- add_person / remove_person / set_person_on：加人、删人、显示或隐藏
- capture_view：保存当前画面
- list_looks / load_look：外观
- list_clothing / load_clothing：服装
- list_poses / load_pose：姿势，person=all 所有人一起换
- list_expressions / set_expression：表情，例如 smile / neutral / surprise
- lock_head：锁住头部
- setup_couple：一次解析两个外观并套成对姿势

不要让用户自己去点 On 或手动删 atom。

### 排错

- status 说插件不存在：VAM 没开，或 Session Plugin 没加 / 没设成用户默认
- 工具超时：enabled 关了，或加到了 Scene Plugin
- Add Plugin 没反应：先开 Enable Plugins
- 重启后插件消失：Set Current As User Defaults
- VaM.exe not found：VAM_ROOT 不是包含 VaM.exe 的目录
- unknown op：插件太旧，更新后 Reload
- 新 Look 看不到：重启 MCP 服务

### 安全

只读写本机文件。工具能加载 VAM_ROOT 下可见的任意场景和预设。不要把这个 MCP 交给不信任的 Agent。

本仓库代码为 [MIT](LICENSE)。Virt-A-Mate 仍受其自己的 EULA 约束。
