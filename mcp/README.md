# SpecSync MCP Git Context Tool

Model Context Protocol (MCP) tool that provides git context to Kiro for SpecSync validation.

## Installation

```bash
npm install -g specsync-mcp-git-context
```

Or use with npx:

```bash
npx specsync-mcp-git-context
```

## Configuration

Add to your Kiro MCP configuration (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "specsync-git": {
      "command": "npx",
      "args": ["specsync-mcp-git-context"],
      "disabled": false
    }
  }
}
```

## Available Tools

### `mcp_specsync_git_get_staged_diff`

Returns git context including:
- Current branch name
- List of staged files
- Full diff of staged changes

**Example Response:**
```json
{
  "branch": "main",
  "stagedFiles": ["backend/handlers/user.py", "backend/models.py"],
  "diff": "diff --git a/backend/handlers/user.py..."
}
```

## Usage with SpecSync

This MCP tool is designed to work with [SpecSync](https://github.com/chryskoum/specsync), a commit-time quality gate that keeps specs, code, tests, and documentation synchronized.

When you commit changes, SpecSync uses this MCP tool to:
1. Read your staged changes
2. Detect drift between specs, code, tests, and docs
3. Generate actionable tasks to fix issues

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run locally
npm start

# Watch mode
npm run dev
```

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Contributing

Contributions welcome! Please see the main [SpecSync repository](https://github.com/chryskoum/specsync) for contribution guidelines.
