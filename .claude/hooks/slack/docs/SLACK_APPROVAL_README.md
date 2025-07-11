# Claude Code Slack Approval System

This system allows you to approve or deny Claude Code operations via Slack, including from your phone or Apple Watch.

## How It Works

1. Claude Code attempts to use a sensitive tool (Write, Edit, MultiEdit)
2. The `pre_tool_use.py` hook intercepts and sends an approval request to Slack
3. You receive a Slack message with Approve/Deny buttons
4. The Node.js bot server handles your button click
5. Claude Code continues or stops based on your decision

## Setup Instructions

### 1. Configure Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app "From scratch"
3. Name it "Claude Code Bot" and select your workspace

### 2. Configure Bot Permissions

1. Go to "OAuth & Permissions"
2. Add these Bot Token Scopes:
   - `chat:write` - To send messages
   - `chat:write.public` - To send to channels without joining

### 3. Enable Socket Mode

1. Go to "Socket Mode" in the left sidebar
2. Enable Socket Mode
3. Generate an app-level token with `connections:write` scope
4. Save the token (starts with `xapp-`)

### 4. Enable Interactivity

1. Go to "Interactivity & Shortcuts"
2. Toggle "Interactivity" ON
3. You can leave the Request URL empty (Socket Mode handles this)

### 5. Install App to Workspace

1. Go to "OAuth & Permissions"
2. Click "Install to Workspace"
3. Authorize the app
4. Copy the Bot User OAuth Token (starts with `xoxb-`)

### 6. Get Signing Secret

1. Go to "Basic Information"
2. Find "Signing Secret" under "App Credentials"
3. Copy the signing secret

### 7. Set Environment Variables

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Claude Code Slack Integration
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"
export SLACK_SIGNING_SECRET="your-signing-secret"
export SLACK_CHANNEL="claude-code"  # or your preferred channel
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### 8. Add Bot to Channel

In Slack, invite your bot to the channel:
```
/invite @Claude Code Bot
```

### 9. Start the Bot Server

```bash
cd ~/.claude/hooks
node start-slack-bot.js

# Or if you haven't installed dependencies yet:
npm install
npm start
```

## Testing

To test the approval system:

1. Make sure the bot server is running
2. Try to edit a file with Claude Code
3. You should receive a Slack message with approval buttons
4. Click Approve or Deny
5. Claude Code should continue or stop accordingly

## Troubleshooting

### Bot not starting
- Check all environment variables are set correctly
- Run `npm install` in the hooks directory
- Check for any error messages in the console

### Messages not appearing
- Verify the bot is in the channel
- Check SLACK_CHANNEL environment variable
- Ensure SLACK_BOT_TOKEN is correct

### Buttons not working
- Make sure the bot server is running
- Check that Socket Mode is enabled
- Verify SLACK_APP_TOKEN is correct
- Check `/tmp/claude-approvals/` directory exists and is writable

### Timeouts
- The default timeout is 60 seconds
- Make sure to respond promptly
- Check that the bot can write to `/tmp/claude-approvals/`

## Running as a Service (Recommended)

### Quick Start with PM2

We've included scripts to make running the bot automatically super easy:

```bash
# Start the bot with PM2 (stays running in background)
./start-bot-pm2.sh

# Check bot status
./bot-status.sh

# View logs
./bot-logs.sh

# Restart bot
./bot-restart.sh

# Stop bot
./bot-stop.sh
```

### Auto-start on System Boot

Since you're on WSL2, the bot won't start automatically when Windows starts. To fix this:

1. **Using Windows Task Scheduler** (Recommended):
   - See `WSL2_AUTOSTART.md` for detailed instructions
   - Creates a Windows task that starts the bot when Windows boots
   - Most reliable method

2. **Using PM2 startup** (Linux only):
   ```bash
   pm2 startup
   # Follow the instructions it provides
   pm2 save
   ```

### Benefits of PM2

- **Auto-restart**: Bot restarts if it crashes
- **Logs management**: Automatic log rotation
- **Resource monitoring**: Track memory and CPU usage
- **Zero downtime**: Bot runs 24/7 in the background
- **Easy management**: Simple commands to control the bot

### Checking if Auto-start Works

After setting up auto-start:
1. Restart your computer
2. Open WSL terminal
3. Run: `./bot-status.sh`
4. Bot should show as "online"