#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

import argparse
import json
import os
import sys
import random

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

try:
    import requests
except ImportError:
    # If requests is not available, we'll handle it gracefully
    requests = None


def send_slack_notification(message):
    """Send notification to Slack channel."""
    if not requests:
        return  # Skip if requests is not available
    
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL', 'claude-code')
    
    if not slack_token:
        return  # No Slack token configured
    
    try:
        # Get engineer name if available
        engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        
        # Create notification message with 30% chance to include name
        if engineer_name and random.random() < 0.3:
            notification_text = f"{engineer_name}, your agent needs your input"
        else:
            notification_text = "Your agent needs your input"
        
        # Send message to Slack
        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            headers={
                'Authorization': f'Bearer {slack_token}',
                'Content-Type': 'application/json'
            },
            json={
                'channel': slack_channel,
                'text': f'🔔 {notification_text}',
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'*Claude Code Notification*\n{notification_text}\n\n*Message:* {message}'
                        }
                    }
                ]
            },
            timeout=10
        )
        
        # Check if the request was successful
        result = response.json()
        if not result.get('ok'):
            # Log error silently - we don't want to interrupt Claude's flow
            pass
            
    except Exception:
        # Fail silently for any errors
        pass


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--notify', action='store_true', help='Enable TTS notifications')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Ensure log directory exists
        import os
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'notification.json')
        
        # Read existing log data or initialize empty list
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Send notification to Slack only if --notify flag is set
        # Always send notifications regardless of message content
        if args.notify:
            message = input_data.get('message', 'Claude needs your input')
            send_slack_notification(message)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()