module.exports = {
  apps: [
    {
      name: 'claude-slack-bot',
      script: '../bot/slack-bot.js',
      cwd: '/mnt/c/dev/cc/.claude/hooks/slack/bot',
      
      // Restart settings
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      
      // Environment variables
      env: {
        NODE_ENV: 'production',
        // These will be loaded from the system environment
        SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
        SLACK_APP_TOKEN: process.env.SLACK_APP_TOKEN,
        SLACK_SIGNING_SECRET: process.env.SLACK_SIGNING_SECRET,
        SLACK_CHANNEL: process.env.SLACK_CHANNEL || 'claude-code'
      },
      
      // Logging
      error_file: '/home/' + process.env.USER + '/.claude/hooks/slack/logs/slack-bot-error.log',
      out_file: '/home/' + process.env.USER + '/.claude/hooks/slack/logs/slack-bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Advanced settings
      instances: 1,
      exec_mode: 'fork',
      
      // Graceful shutdown
      kill_timeout: 3000,
      listen_timeout: 3000,
      
      // Memory management
      max_memory_restart: '500M'
    }
  ]
}