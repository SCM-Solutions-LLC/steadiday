# Claude Code project configuration

This directory configures [Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web)
for everyone working in this repo.

## Plugins

`settings.json` declares the official Anthropic plugin marketplace
(`claude-plugins-official`) and enables these plugins automatically when the
project is opened in Claude Code:

| Plugin | What it adds |
| --- | --- |
| `frontend-design` | Frontend/UI design guidance |
| `superpowers` | General-purpose workflow skills |
| `context7` | Up-to-date library documentation lookup (MCP) |
| `playwright` | Browser automation / testing (MCP) |
| `expo` | Expo / React Native skills + EAS MCP server |
| `ralph-loop` | Run a prompt/command on a recurring loop for autonomous tasks |

No manual `claude plugin install` is needed once this file is present — opening
the project enables them.

## Secrets / authentication (not committed)

Some plugins need credentials that must **not** be checked into the repo:

- **context7** — works without a key (rate-limited). For higher limits, get a
  free key at https://context7.com/dashboard and provide it locally, e.g. run
  the MCP with `--api-key <key>` or set it in your personal (non-committed)
  Claude Code config.
- **expo** — its MCP server (`https://mcp.expo.dev/mcp`) uses OAuth. Run `/mcp`
  in an interactive Claude Code session and authenticate the `expo` server with
  your Expo account.
