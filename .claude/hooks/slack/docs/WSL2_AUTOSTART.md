# Auto-starting Claude Slack Bot on Windows/WSL2

Since WSL2 doesn't automatically start services, here are several methods to auto-start the bot when Windows starts.

## Method 1: Windows Task Scheduler (Recommended)

1. Open Windows Task Scheduler
2. Create a new task (not basic task):
   - **General Tab:**
     - Name: "Claude Slack Bot WSL2"
     - Check "Run whether user is logged on or not"
     - Check "Run with highest privileges"
   
   - **Triggers Tab:**
     - New → Begin the task: "At startup"
     - Delay task for: 30 seconds (gives WSL time to initialize)
   
   - **Actions Tab:**
     - New → Action: "Start a program"
     - Program: `C:\Windows\System32\wsl.exe`
     - Arguments: `-d Ubuntu -u yourusername -- /home/yourusername/.claude/hooks/slack/scripts/start-bot-pm2.sh`
     - (Replace "Ubuntu" with your WSL distro name and "yourusername" with your username)
   
   - **Conditions Tab:**
     - Uncheck "Start the task only if the computer is on AC power"
   
   - **Settings Tab:**
     - Check "Allow task to be run on demand"
     - Check "If the task fails, restart every: 5 minutes"

## Method 2: Windows Startup Script (Batch File)

Create `C:\Users\YourWindowsUsername\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\claude-bot.bat`:

```batch
@echo off
timeout /t 30 /nobreak > nul
wsl -d Ubuntu -u yourusername -- bash -lc "cd /home/yourusername/.claude/hooks/slack/scripts && ./start-bot-pm2.sh"
```

## Method 3: Windows Terminal Profile

Add to Windows Terminal settings.json:

```json
{
  "profiles": {
    "list": [
      {
        "name": "Claude Bot",
        "commandline": "wsl.exe -d Ubuntu -- /home/yourusername/.claude/hooks/slack/scripts/start-bot-pm2.sh",
        "hidden": true,
        "startingDirectory": "//wsl$/Ubuntu/home/yourusername/.claude/hooks/slack/scripts"
      }
    ]
  }
}
```

Then create a shortcut that runs: `wt -w _new -p "Claude Bot"`

## Method 4: WSL2 systemd (if enabled)

If you have systemd enabled in WSL2:

1. Create service file:
```bash
sudo nano /etc/systemd/system/claude-slack-bot.service
```

2. Add:
```ini
[Unit]
Description=Claude Slack Bot
After=network.target

[Service]
Type=forking
User=yourusername
Environment="HOME=/home/yourusername"
ExecStart=/home/yourusername/.claude/hooks/slack/scripts/start-bot-pm2.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable:
```bash
sudo systemctl enable claude-slack-bot
sudo systemctl start claude-slack-bot
```

## Verifying Auto-start

After setting up auto-start:

1. Restart Windows
2. Wait about 1 minute
3. Open WSL terminal
4. Run: `cd ~/.claude/hooks/slack/scripts && ./bot-status.sh`

The bot should show as "online".

## Troubleshooting

If the bot doesn't start:

1. Check Windows Event Viewer for Task Scheduler errors
2. Verify WSL is starting: `wsl --list --running`
3. Check PM2 logs: `pm2 logs claude-slack-bot`
4. Ensure environment variables are in ~/.bashrc
5. Test manual start: `cd ~/.claude/hooks/slack/scripts && ./start-bot-pm2.sh`

## Quick Test

To test without restarting Windows:
```powershell
# In PowerShell
wsl -d Ubuntu -u yourusername -- /home/yourusername/.claude/hooks/slack/scripts/start-bot-pm2.sh
```