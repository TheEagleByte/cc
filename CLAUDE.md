# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code configuration repository containing custom settings, commands, and MCP server integrations to enhance the Claude Code development experience.

## Essential Commands

### Git Operations
- **Commit code**: Use `/commit` to create well-formatted commits with conventional commit messages and emoji
  - Important: Do not include the "Co-authored by Claude Code" part when committing
  - The command automatically runs pre-commit checks (lint, build) unless `--no-verify` is specified
  - If no files are staged, it will automatically stage all modified files

### GitHub Operations  
- **Create PR**: `/github/pr-create` - Creates a pull request with proper formatting
- **Review PR**: `/github/pr-review` - Reviews and provides feedback on pull requests

### GitLab Operations
- **Create PR**: `/gitlab/pr-create` - Creates a merge request with proper formatting  
- **Review PR**: `/gitlab/pr-review` - Reviews and provides feedback on merge requests

## MCP Server Usage

### context7
Use for accessing up-to-date code examples and documentation:
- Command: `mcp__context7__resolve-library-id` and `mcp__context7__get-library-docs`

### playwright
Use for checking UI changes through a browser:
- Provides browser automation capabilities for testing visual changes

### sequential-thinking
Use for breaking down and working through complex problems and task lists:
- Command: `mcp__sequential-thinking__sequentialthinking`

### basic-memory
Provides persistent memory capabilities across sessions

## Allowed Operations

The configuration restricts operations to a specific allowlist including:
- File operations: Write, Edit
- Git operations: `git add` only
- Package managers: yarn/npm/pnpm commands for build, lint, test, start
- Dotnet: build, restore, clean, test commands
- GitHub CLI: pr commands
- Safe bash commands: cat, cp, find, grep, ls, rg, sed, tail, echo, mkdir

## Development Setup Dependencies

When setting up this configuration on a new system:
1. Node.js v22 (via nvm)
2. Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
3. UV (Python package manager)
4. Homebrew (on Linux/WSL)
5. GitHub CLI (gh) - authenticate with `gh auth login`
6. GitLab CLI (glab) - authenticate with `glab auth login`

## WSL-Specific Configuration

When using git within WSL, set line ending handling:
```bash
git config --global core.autocrlf true
```

## Configuration Structure

- `.claude/settings.json` - Main configuration with permissions
- `.claude/settings.local.json` - Local overrides (not tracked)
- `.claude/commands/` - Custom slash commands
- `.claude/hooks/` - Hook scripts for Claude Code events
  - `notification.py` - Sends notifications to Slack (requires SLACK_BOT_TOKEN)
  - `slack/` - Optional approval workflow hooks for Slack integration
- `.mcp.json` - MCP server configurations

## Slack Integration

The notification hook has been updated to send messages to Slack instead of using TTS. To enable:
1. Set `SLACK_BOT_TOKEN` environment variable with your bot token
2. Set `SLACK_CHANNEL` (optional, defaults to 'claude-code')
3. See `SLACK_SETUP.md` for detailed setup instructions