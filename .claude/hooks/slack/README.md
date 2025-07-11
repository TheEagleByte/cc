# Claude Code Slack Integration

This directory contains all components for the Slack approval system for Claude Code.

## Directory Structure

```
slack/
├── bot/                    # Node.js Slack bot application
│   ├── slack-bot.js       # Main bot server
│   ├── package.json       # Node.js dependencies
│   └── node_modules/      # (created after npm install)
│
├── scripts/               # Management and automation scripts
│   ├── start-bot-pm2.sh   # Start bot with PM2
│   ├── bot-status.sh      # Check bot status
│   ├── bot-logs.sh        # View bot logs
│   ├── bot-restart.sh     # Restart bot
│   ├── bot-stop.sh        # Stop bot
│   └── ecosystem.config.js # PM2 configuration
│
├── docs/                  # Documentation
│   ├── SLACK_APPROVAL_README.md  # Complete setup guide
│   └── WSL2_AUTOSTART.md        # Windows auto-start instructions
│
├── logs/                  # Log files (created automatically)
│
├── slack-notify-only.py   # Notification-only hook
├── slack-wait-approval.py # Approval-waiting hook
└── README.md             # This file
```

## Quick Start

1. **First-time setup:**
   ```bash
   cd ~/.claude/hooks/slack/scripts
   ./start-bot-pm2.sh
   ```

2. **Check status:**
   ```bash
   ./bot-status.sh
   ```

3. **View logs:**
   ```bash
   ./bot-logs.sh
   ```

## Documentation

- For complete setup instructions: see `docs/SLACK_APPROVAL_README.md`
- For auto-start configuration: see `docs/WSL2_AUTOSTART.md`

## How It Works

1. Claude Code attempts a sensitive operation (Write/Edit)
2. The `pre_tool_use.py` hook calls the Slack approval function
3. A message with Approve/Deny buttons is sent to Slack
4. The Node.js bot handles button clicks
5. The approval decision is written to `/tmp/claude-approvals/`
6. Claude Code continues or stops based on the decision