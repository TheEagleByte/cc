#!/bin/bash
# Restart Claude Slack bot

if ! command -v pm2 &> /dev/null; then
    echo "PM2 is not installed. Run: npm install -g pm2"
    exit 1
fi

echo "Restarting Claude Slack bot..."
pm2 restart claude-slack-bot
pm2 show claude-slack-bot