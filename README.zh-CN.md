# VamMCP

非官方 [MCP](https://modelcontextprotocol.io/) 服务 + Virt-A-Mate **Session 插件**。用对话加载你本机库里已经有的场景、Look 和服装预设。

与 Mesh VR / Virt-A-Mate **无隶属关系**。你需要自己拥有合法的 VAM 或 VaMX。仅限 18 岁以上成年人。详见 [NOTICE.md](NOTICE.md)。

**不能生成角色或衣服**，只能搜索并加载硬盘上已有的文件。

## 原理

```
MCP 客户端  →  vam-mcp（Python）  →  Saves/PluginData/vam-mcp/*.json  →  VamMcpBridge（Session 插件）  →  SuperController
```

第一版走本地文件桥，不依赖 VAM 里的 HTTP。

## 环境

- Windows
- Virt-A-Mate 1.20+ 或带 `VaM.exe` 的 VaMX
- Python 3.10+（建议 [uv](https://github.com/astral-sh/uv)）
- 任意 MCP 客户端（Grok、Claude Desktop、Cursor 等）

## 安装

### 1. 插件

**发布版：** 把 Releases 里的 `VamMcp.Bridge.N.var` 放进 `AddonPackages`。

**开发版：** 在本仓库执行：

```powershell
.\scripts\install-dev.ps1 -VamRoot "E:\VaMX"
```

然后在 VAM 里：

1. 主界面 → **Session Plugins** → Add Plugin → `Custom/Scripts/VamMcp/Bridge/VamMcpBridge.cs`
2. Session Plugin Presets → 设成 user default（重启后桥还在）
3. 保持 VAM 开着

换场景会毁掉 Scene Plugin，所以必须加在 **Session Plugins**。

### 2. MCP

```powershell
cd mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

客户端配置里把 `VAM_ROOT` 指到包含 `VaM.exe` 的目录。本机示例见 [examples/grok.mcp.json](examples/grok.mcp.json)。

### 3. 连通测试

VAM 已开、插件已加载时：

```powershell
.\scripts\ping-bridge.ps1 -VamRoot "E:\VaMX"
```

## 工具

| 工具 | 作用 |
| --- | --- |
| `status` | 插件是否在线 |
| `list_scenes` / `load_scene` | 搜 / 加载场景 |
| `list_persons` | 当前场景里的人物 |
| `list_looks` / `load_look` | 搜 / 加载外观预设 |
| `list_clothing` / `load_clothing` | 搜 / 加载服装预设 |

先 `list_*` 拿到精确 `path`，再 `load_*`。

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
