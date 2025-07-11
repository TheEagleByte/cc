#!/bin/bash
# Start the Claude Slack bot with PM2
# This script ensures environment variables are loaded and PM2 is installed

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Claude Code Slack Bot - PM2 Startup${NC}"
echo "===================================="

# Source the user's profile to get environment variables
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
fi

# Check for required environment variables
MISSING_VARS=()
[ -z "$SLACK_BOT_TOKEN" ] && MISSING_VARS+=("SLACK_BOT_TOKEN")
[ -z "$SLACK_APP_TOKEN" ] && MISSING_VARS+=("SLACK_APP_TOKEN")
[ -z "$SLACK_SIGNING_SECRET" ] && MISSING_VARS+=("SLACK_SIGNING_SECRET")

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}Error: Missing required environment variables:${NC}"
    printf '%s\n' "${MISSING_VARS[@]}"
    echo -e "\n${YELLOW}Please add these to your ~/.bashrc or ~/.zshrc${NC}"
    exit 1
fi

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}PM2 not found. Installing PM2 globally...${NC}"
    npm install -g pm2
fi

# Navigate to hooks directory
cd "$(dirname "$0")"

# Check if node_modules exists in bot directory
if [ ! -d "../bot/node_modules" ]; then
    echo -e "${YELLOW}Installing bot dependencies...${NC}"
    cd ../bot
    npm install
    cd ../scripts
fi

# Create logs directory
mkdir -p ../logs

# Stop any existing instance
pm2 stop claude-slack-bot 2>/dev/null || true
pm2 delete claude-slack-bot 2>/dev/null || true

# Start the bot with PM2
echo -e "${GREEN}Starting Claude Slack bot with PM2...${NC}"
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Show status
echo -e "\n${GREEN}Bot started successfully!${NC}"
pm2 show claude-slack-bot

echo -e "\n${BLUE}Useful PM2 commands:${NC}"
echo "  pm2 status              - Check bot status"
echo "  pm2 logs claude-slack-bot  - View bot logs"
echo "  pm2 restart claude-slack-bot - Restart the bot"
echo "  pm2 stop claude-slack-bot    - Stop the bot"
echo "  pm2 monit               - Real-time monitoring"

# Check if PM2 startup is configured
if ! pm2 startup | grep -q "already"; then
    echo -e "\n${YELLOW}To start PM2 on system boot:${NC}"
    echo "Run: pm2 startup"
    echo "Then follow the instructions provided"
fi