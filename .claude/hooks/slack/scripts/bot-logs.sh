#!/bin/bash
# View logs for Claude Slack bot

if ! command -v pm2 &> /dev/null; then
    echo "PM2 is not installed. Run: npm install -g pm2"
    exit 1
fi

echo "Claude Slack Bot Logs (Press Ctrl+C to exit)"
echo "==========================================="
pm2 logs claude-slack-bot --lines 50