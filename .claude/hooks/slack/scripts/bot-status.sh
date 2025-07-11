#!/bin/bash
# Quick status check for Claude Slack bot

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Claude Slack Bot Status${NC}"
echo "======================="

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo -e "${RED}PM2 is not installed${NC}"
    echo "Run: npm install -g pm2"
    exit 1
fi

# Get bot status
STATUS=$(pm2 jlist 2>/dev/null | jq -r '.[] | select(.name == "claude-slack-bot") | .pm2_env.status' 2>/dev/null)

if [ -z "$STATUS" ]; then
    echo -e "${RED}Bot is not running${NC}"
    echo -e "\nTo start the bot, run:"
    echo "  ./start-bot-pm2.sh"
else
    if [ "$STATUS" = "online" ]; then
        echo -e "${GREEN}Bot is running${NC}"
        
        # Get detailed info
        pm2 show claude-slack-bot | grep -E "(status|uptime|restarts|memory|created at)"
        
        echo -e "\n${BLUE}Recent logs:${NC}"
        pm2 logs claude-slack-bot --lines 5 --nostream
    else
        echo -e "${YELLOW}Bot status: $STATUS${NC}"
        pm2 show claude-slack-bot
    fi
fi

echo -e "\n${BLUE}Quick commands:${NC}"
echo "  ./bot-logs.sh    - View logs"
echo "  ./bot-restart.sh - Restart bot"
echo "  ./bot-stop.sh    - Stop bot"