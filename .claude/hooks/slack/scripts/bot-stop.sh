#!/bin/bash
# Stop Claude Slack bot

if ! command -v pm2 &> /dev/null; then
    echo "PM2 is not installed. Run: npm install -g pm2"
    exit 1
fi

echo "Stopping Claude Slack bot..."
pm2 stop claude-slack-bot
echo "Bot stopped. To start again, run: ./start-bot-pm2.sh"