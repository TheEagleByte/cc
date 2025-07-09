# CC

Personal repo containing all my common CC stuff

## Copy Everything to User Config

The following copies the claude commands/configuration from this repo to your user config directory.

```bash
cp -r .claude/* ~/.claude/
cp .mcp.json ~/.mcp.json

# If you don't use gitlab, remove those commands
rm ~/.claude/commands/gitlab

# If you don't use github, remove those commands
rm ~/.claude/commands/github
```

## Dependencies

1. [Node.js](https://nodejs.org/en/download)

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

# Verify the Node.js version:
node -v # Should print "v22.17.0".
nvm current # Should print "v22.17.0".

# Verify npm version:
npm -v # Should print "10.9.2".
```

2. [Claude Code](https://docs.anthropic.com/en/docs/claude-code/setup)

```bash
npm install -g @anthropic-ai/claude-code
```

3. [UV](https://docs.astral.sh/uv/getting-started/installation/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

4. [GitHub CLI](https://github.com/cli/cli/blob/trunk/docs/install_linux.md):

```bash
brew install gh
gh auth login
```

5. [GitLab CLI](https://gitlab.com/gitlab-org/cli):

```bash
brew install glab
glab auth login
```

## Other MCP Servers

- [Figma](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server)
- [Atlassian](https://community.atlassian.com/forums/Atlassian-Platform-articles/Using-the-Atlassian-Remote-MCP-Server-beta/ba-p/3005104)
- [Supabase](https://github.com/supabase-community/supabase-mcp)
