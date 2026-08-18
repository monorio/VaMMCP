# vam-mcp (Python package)

Unofficial MCP server for Virt-A-Mate.

Install and client config (Codex, Claude Code, Cursor, Grok, Copilot) are in
the repository root. Agents should follow [AGENTS.md](../AGENTS.md?plain=1):

- [README.md](../README.md) (English)
- [中文说明](../docs/zh-CN.md)

```bash
# from this directory
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
# or: uv run vam-mcp
```

Set `VAM_ROOT` to the folder that contains `VaM.exe`. Keep VAM running with
`VamMcpBridge` loaded as a **Session Plugin** from the loose path
`VAM_ROOT\Custom\Scripts\VamMcp\Bridge\VamMcpBridge.cs`.
