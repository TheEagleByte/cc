# Slack Integration for Claude Code Hooks

This setup enables Claude Code to send notifications to Slack when it needs your input or when performing operations. You can also configure approval workflows for sensitive operations.

## Prerequisites

1. A Slack workspace where you can add apps
2. Python with `uv` package manager installed
3. Claude Code with hooks support

## Basic Setup (Notifications Only)

### 1. Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Give your app a name (e.g., "Claude Code Bot")
4. Select your workspace

### 2. Configure Bot Permissions

1. Go to "OAuth & Permissions" in the left sidebar
2. Scroll to "Scopes" → "Bot Token Scopes"
3. Add these scopes:
   - `chat:write` - To send messages
   - `chat:write.public` - To send to channels without joining

### 3. Install App to Workspace

1. Go to "OAuth & Permissions"
2. Click "Install to Workspace"
3. Authorize the app
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 4. Set Environment Variables

For WSL, add these to your `~/.bashrc` or `~/.zshrc` file so they're set every time you launch WSL:

```bash
# Claude Code Slack Integration
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_CHANNEL="claude-code"  # or your preferred channel
export ENGINEER_NAME="Your Name"    # Optional: for personalized messages
```

After adding these lines, reload your shell configuration:
```bash
source ~/.bashrc  # or source ~/.zshrc if using zsh
```

Alternatively, you can add them to `/etc/environment` for system-wide availability in WSL.

### 5. Add Bot to Channel

In Slack, invite your bot to the channel:
```
/invite @Claude Code Bot
```

### 6. Test the Integration

The updated `notification.py` will now send messages to Slack instead of using TTS.

## Advanced Setup (With Approvals)

For approval workflows (like in the Medium article), you need to run a separate bot service.

### 1. Update Hook Configuration

Edit your `.claude/settings.json` to use the approval hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^(Write|Edit|MultiEdit)$",
        "hooks": [
          {
            "type": "command",
            "command": "uv run .claude/hooks/slack/slack-wait-approval.py"
          }
        ]
      },
      {
        "matcher": "^(Bash|Grep|Glob|LS)$",
        "hooks": [
          {
            "type": "command", 
            "command": "uv run .claude/hooks/slack/slack-notify-only.py"
          }
        ]
      }
    ]
  }
}
```

### 2. Enable Slack Interactivity

1. In your Slack app settings, go to "Interactivity & Shortcuts"
2. Toggle "Interactivity" ON
3. Set Request URL to your bot server endpoint (see below)

### 3. Run the Bot Server

For development with Socket Mode:

1. Go to "Socket Mode" in your app settings
2. Enable Socket Mode
3. Generate an app-level token with `connections:write` scope
4. Add to your environment:
   ```bash
   export SLACK_APP_TOKEN="xapp-your-app-token"
   ```
5. Install dependencies and run:
   ```bash
   pip install slack-bolt python-dotenv
   python .claude/hooks/slack-bot-example.py
   ```

For production, deploy the bot to a web server and use the Web API instead.

## How It Works

### Notification Flow
1. Claude Code triggers a hook event
2. `notification.py` receives the event details
3. Sends a formatted message to your Slack channel
4. You see the notification on all your devices

### Approval Flow
1. Claude tries to use a sensitive tool (Write/Edit)
2. `slack-wait-approval.py` sends message with Approve/Deny buttons
3. You click a button in Slack (on phone, watch, or desktop)
4. Bot server writes decision to `/tmp/claude-approvals/{session_id}.json`
5. Hook reads the decision and returns it to Claude
6. Claude proceeds or stops based on your decision

## Troubleshooting

### Messages not appearing in Slack
- Check that `SLACK_BOT_TOKEN` is set correctly
- Verify the bot is in the channel
- Check that the channel name matches `SLACK_CHANNEL`

### Approval buttons not working
- Ensure the bot server is running
- Check that interactivity is enabled in your Slack app
- Verify `/tmp/claude-approvals/` directory is writable

### Timeouts on approvals
- The default timeout is 60 seconds
- Make sure to respond to approval requests promptly
- Check that the bot server can write to the approval directory

## Security Notes

- Keep your Slack tokens secure and never commit them
- The `/tmp/claude-approvals/` directory should be accessible only by your user
- Review all hooks before enabling them
- Consider using more restrictive matchers for sensitive operations