# VamMCP

[English](README.md) | [中文](README_zh-CN.md)

> **Agent（Codex、Claude Code、Cursor、Grok、Copilot 等）：先读 [AGENTS.md](AGENTS.md) 并按它操作。** 不要只凭本 README 自己猜 VAM 流程。

非官方 [MCP](https://modelcontextprotocol.io/) 服务 + Virt-A-Mate **Session 插件**。用对话加载你本机库里已经有的场景、Look、服装、姿势和表情。

与 Mesh VR / Virt-A-Mate **无隶属关系**。你需要自己拥有合法的 VAM 或 VaMX。详见 [NOTICE.md](NOTICE.md)。

**不能生成角色或衣服**，只能搜索并加载硬盘上已有的文件。

当前版本：

| 组件 | 版本 |
| --- | --- |
| Session 插件 `VamMcpBridge` | 0.5.1 |
| Python 包 `vam-mcp` | 0.2.0 |

## 原理

```
MCP 客户端  →  vam-mcp（Python）  →  Saves/PluginData/vam-mcp/*.json  →  VamMcpBridge（Session 插件）  →  SuperController
```

第一版走本地文件桥，不依赖 VAM 里的 HTTP，也不监听网络端口。

## 环境

- Windows
- Virt-A-Mate **1.20+**，或安装目录里有 `VaM.exe` 的 VaMX
- Python **3.10+**（可选 [uv](https://github.com/astral-sh/uv)）
- 任意支持 MCP 的客户端 / 编程 Agent（Codex、Claude Code、Cursor、Grok、Copilot 等）
- 本机 VAM 里已经有对应的场景 / Look / 服装 / 姿势

`setup_couple` 额外依赖：本机要有成对的 F/M 姿势文件（服务端目前查找 `vamX.1.52:/Custom/Atom/Person/Pose/...`）。表情别名还需要角色身上已有对应 morph。缺文件时工具会在 `missing` 里列出，不会凭空捏脸。

## 安装（按这个顺序）

两边都要装：VAM 里的插件，以及 Python MCP 服务。插件必须加在 **Session Plugins**，不要加到 Scene Plugins，也不要加在某个 Person 身上。

### 1. 先在 VAM 里允许插件

1. 启动 VAM / VaMX。
2. 打开主界面（`Esc`）。
3. **User Preferences → Security**（用户偏好 → 安全）。
4. 打开 **Enable Plugins**。
5. 建议同时打开 **Plugins Always Enabled**，避免每次启动都弹「是否允许该插件」。

这一步没开的话，后面 `Add Plugin` 会没有入口，或者脚本加进去也不跑。

### 2. 安装 VamMcpBridge 插件

#### 方式 A — `.var` 包（日常用这个）

1. 拿到 `VamMcp.Bridge.N.var`：
   - 从 [Releases](../../releases) 下载，或
   - 在本仓库执行 `.\scripts\pack-var.ps1 -Version 1`（生成 `dist-var\VamMcp.Bridge.1.var`）。
2. 把这个文件复制到 `VaM.exe` 旁边的 **`AddonPackages`** 目录：

   ```
   <VAM_ROOT>\AddonPackages\VamMcp.Bridge.1.var
   ```

3. 如果 VAM 当时是开着的，**重启一次**，让它重新扫描包。

#### 方式 B — 开发版（直接用本仓库源码）

在仓库根目录执行：

```powershell
.\scripts\install-dev.ps1 -VamRoot "E:\VaMX"
```

脚本会把 `plugin\` 目录联接（失败则复制）到：

```
<VAM_ROOT>\Custom\Scripts\VamMcp\Bridge\VamMcpBridge.cs
```

以后改了 `.cs`，在 **Session Plugins** 里对 `VamMcpBridge` 点 **Reload** 即可，不必重启 VAM。

### 3. 在游戏里启用插件

换场景会毁掉 Scene Plugin，所以必须加在 **Session Plugins**。

1. 启动 VAM，按 `Esc` 打开主界面。
2. 打开主菜单上紫色的 **Session Plugins** 页（不要点到某个角色身上的 Plugins）。
3. 点 **Add Plugin**。
4. 在文件浏览器里选 `VamMcpBridge.cs`：
   - `.var` 安装：包名 **`VamMcp.Bridge`** → `Custom/Scripts/VamMcp/Bridge/VamMcpBridge.cs`
   - 开发安装：`Custom/Scripts/VamMcp/Bridge/VamMcpBridge.cs`
5. 如果弹出是否允许插件，选 **Allow**。
6. 确认列表里出现这一行，并且：
   - **`enabled`** 开关是打开的
   - 状态文字类似 `ready  root=...`
7. 让它下次启动还在：
   - 还在 Session Plugins 面板里，打开 **Session Plugin Presets**
   - **Change User Defaults → Set Current As User Defaults**（把当前设为用户默认）

不设默认的话，下次开 VAM 桥就没了。

保持 VAM 开着。MCP 只有在插件已加载且 `enabled` 打开时才会响应。

### 4. 安装 Python MCP 服务

```powershell
cd E:\VamMCP\mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

客户端配置里的 `VAM_ROOT` 必须指向**包含 `VaM.exe` 的目录**，例如 `E:\VaMX`。

用 [uv](https://github.com/astral-sh/uv) 可以不建 venv，直接 `uv --directory E:\VamMCP\mcp run vam-mcp`。

### 5. 配置 Agent / MCP 客户端

两处路径都要改：`command` 是本仓库 venv 里的 Python，`VAM_ROOT` 是 VAM / VaMX 安装目录。改完后重启 Agent，或刷新它的 MCP 列表。

请把 **本仓库** 当作工作区打开，这样 Agent 会自动加载 [AGENTS.md](AGENTS.md)。

#### Codex（CLI / IDE）

把 [examples/codex.config.toml](examples/codex.config.toml) 追加到 `%USERPROFILE%\.codex\config.toml`（或项目里的 `.codex\config.toml`）：

```toml
[mcp_servers.vam]
command = 'E:\VamMCP\mcp\.venv\Scripts\python.exe'
args = ["-m", "vam_mcp.server"]

[mcp_servers.vam.env]
VAM_ROOT = 'E:\VaMX'
```

或：

```powershell
codex mcp add vam --env VAM_ROOT=E:\VaMX -- E:\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server
```

然后 `cd` 进本仓库再启动 Codex。它会自动读 `AGENTS.md`。

#### Grok

把 [examples/grok.config.toml](examples/grok.config.toml) 追加到 `%USERPROFILE%\.grok\config.toml`（或项目里的 `.grok\config.toml`）：

```toml
[mcp_servers.vam]
command = 'E:\VamMCP\mcp\.venv\Scripts\python.exe'
args = ["-m", "vam_mcp.server"]
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120

[mcp_servers.vam.env]
VAM_ROOT = 'E:\VaMX'
```

或执行 `grok mcp add vam -e VAM_ROOT=E:\VaMX -- E:\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server`。在 Grok 里执行 `/mcps` 并按 `r` 刷新。

#### Claude Code

```powershell
claude mcp add vam --env VAM_ROOT=E:\VaMX -- E:\VamMCP\mcp\.venv\Scripts\python.exe -m vam_mcp.server
```

Claude Code 会读 `AGENTS.md`。把本仓库当作项目打开即可。

#### Cursor、Copilot 和其它 JSON 客户端

格式与 [examples/claude_desktop.json](examples/claude_desktop.json)、[examples/grok.mcp.json](examples/grok.mcp.json) 相同：

```json
{
  "mcpServers": {
    "vam": {
      "command": "E:\\VamMCP\\mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "vam_mcp.server"],
      "env": { "VAM_ROOT": "E:\\VaMX" }
    }
  }
}
```

| 客户端 | 配置文件 |
| --- | --- |
| Codex | `%USERPROFILE%\.codex\config.toml` |
| Grok | `%USERPROFILE%\.grok\config.toml` |
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `%USERPROFILE%\.cursor\mcp.json` 或项目下 `.cursor\mcp.json` |
| VS Code Copilot | 用户/工作区 `mcp.json` 里的 MCP 段 |
| 会读 `.mcp.json` 的 Agent | 项目根目录 `.mcp.json`（JSON 同上） |

改完后应能看到名为 `vam` 的服务，以及 `status`、`list_scenes`、`setup_couple` 等工具。

### 6. 连通测试

VAM 已开、插件已加载时：

```powershell
.\scripts\ping-bridge.ps1 -VamRoot "E:\VaMX"
```

返回带 `"ok": "true"` 和 `"plugin": "VamMcpBridge"` 的 JSON 就说明文件桥通了。然后再让 Agent 调用一次 `status`。

## 日常怎么用

1. **先开 VAM**，等到 Session Plugin 状态变成 `ready`。
2. 在 **本仓库** 里启动 Agent，让它读到 [AGENTS.md](AGENTS.md)。
3. 直接说话。Agent 应先 `list_*` 再 `load_*`；两个人加进当前房间并套成对姿势走 `setup_couple`。

可以这样说：

- 「当前场景里有哪些人？」
- 「搜一下这个名字的外观并加载。」
- 「把这两个人加进当前房间并坐下。」
- 「给她换成微笑。」
- 「头一直跟着镜头转，锁住头。」

场景 / 外观 / 姿势变更后，服务端会把当前画面存到 `Saves/PluginData/vam-mcp/preview.png`。需要核对结果时让 Agent 再调一次 `capture_view`。

常规流程：先 `list_*` 拿到精确 `path`，再 `load_*`。换脸用 `set_expression`（需要插件 **0.5.0+**）。头跟着镜头转就调 `lock_head`（需要插件 **0.5.1+**）。改完 `VamMcpBridge.cs` 后，在 Session Plugins 里 **Reload**。

## 工具

| 工具 | 作用 |
| --- | --- |
| `status` | `VAM_ROOT` 是否有效、插件是否在线 |
| `list_scenes` / `load_scene` | 搜 / 加载场景（`merge=true` 合并进当前场景） |
| `list_persons` | 当前场景里的人物 |
| `add_person` / `remove_person` / `set_person_on` | 加人、删人、显示/隐藏 |
| `capture_view` | 把当前画面存到 `Saves/PluginData/vam-mcp/preview.png` |
| `list_looks` / `load_look` | 搜 / 加载外观预设 |
| `list_clothing` / `load_clothing` | 搜 / 加载服装预设 |
| `list_poses` / `load_pose` | 搜 / 加载姿势（`person=all` 所有人一起换） |
| `list_expressions` / `set_expression` | 列表情别名 / 脸上 morph，再换表情（`smile`、`neutral`、`surprise` 等） |
| `lock_head` | 锁住头部，不让它跟着镜头转 |
| `setup_couple` | 一次做完：解析两个外观、打开或加人，再套成对姿势 |

不要让用户自己去点 On 或手动删 atom，用 `set_person_on` / `remove_person`。

## 已知限制

- 场景目录在 MCP 进程生命周期内会缓存。往 VAM 里新丢了 `.var` 或 Look 之后，重启 MCP 才能让 `list_*` 看到。
- `setup_couple` 的成对姿势路径目前按 **vamX 1.52** 写。只有别的版本、没有 1.52 时，那两次 `load_pose` 会失败。
- `set_expression` 只能驱动角色身上已经有的 morph。缺的会进 `missing`，脸不会变。
- `lock_head` 会固定头/颈控制器并把眼睛设成 Target。角色上如果挂了视线追踪类插件，头仍可能转 —— 关掉那个插件，或等它加载完再锁一次。
- `add_person` 只是启动 VAM 协程，马上返回。`setup_couple` 大约等 2 秒；机器慢的话可能要再试一次。
- `list_*` / `load_*` 不会去 Hub 下载内容。磁盘上没有，就只能报 not found。

## 排错

| 现象 | 先查什么 |
| --- | --- |
| `status` 说插件不存在 | VAM 没开，或 Session Plugin 没加 / 没设成用户默认 |
| MCP 工具超时 | 插件的 `enabled` 关了；VAM 卡在加载界面；或者加到了 Scene Plugin，换场景后被销毁 |
| `Add Plugin` 没反应 | **User Preferences → Security → Enable Plugins** |
| 重启后插件消失 | Session Plugin Presets → **Set Current As User Defaults** |
| `VaM.exe not found` | `VAM_ROOT` 不是包含 `VaM.exe` 的那个目录 |
| `unknown op: set_expression` / `lock_head` | 插件太旧。更新 `.cs` / `.var` 后在 Session Plugins 里 **Reload**（分别需要 0.5.0+ / 0.5.1+） |
| 新 Look 在 `list_looks` 里看不到 | 重启 MCP 服务，让它重新扫描 `AddonPackages` |
| `setup_couple` 套姿势失败 | 改用 `list_poses` / `load_pose`，或安装服务端期望的成对姿势包 |
| ping 脚本没响应 | 同超时：VAM 在跑、Session Plugin 已加载、`enabled` 打开 |
| Agent 不用 VAM 工具 | 工作区不是本仓库（没读到 `AGENTS.md`），或 `vam` MCP 没连上 |

## 打开发包

```powershell
.\scripts\pack-var.ps1 -Version 1
```

Git 只提交源码。`.var` 放到 GitHub Release，不要提交进仓库，也不要提交 Look、场景或整个 VAM 安装目录。

第一次公开推送前，把 `plugin/meta.json` 里的作者名和仓库地址改成你的 GitHub 账号。

## 安全

- 只读写本机文件，不监听网络。
- 工具能加载 `VAM_ROOT` 下可见的任意场景和预设，等于控制整场会话。
- 不要把这个 MCP 交给不信任的 Agent，也不要对外暴露 `Saves/PluginData/vam-mcp`。

## 许可

本仓库代码为 [MIT](LICENSE)。Virt-A-Mate 仍受其自己的 EULA 约束。
