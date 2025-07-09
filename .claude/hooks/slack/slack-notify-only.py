#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

"""
Slack notification hook for safe Claude Code operations.
Sends a notification to Slack without requiring approval.
Used for tools like Grep, LS, Bash that are considered safe.
"""

import json
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests
except ImportError:
    print('{"continue": true}')  # Continue if requests not available
    sys.exit(0)


def main():
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extract relevant information
        session_id = input_data.get('session_id', 'unknown')
        tool_name = input_data.get('tool_name', 'unknown')
        tool_input = input_data.get('tool_input', {})
        
        # Get Slack configuration
        slack_token = os.getenv('SLACK_BOT_TOKEN')
        slack_channel = os.getenv('SLACK_CHANNEL', 'claude-code')
        
        if not slack_token:
            # No Slack token, just continue
            print('{"continue": true}')
            sys.exit(0)
        
        # Format the message based on tool type
        if tool_name == 'Bash':
            command = tool_input.get('command', 'N/A')
            description = tool_input.get('description', 'No description')
            message_text = f"🔔 Claude ran: `{tool_name}`"
            detail_text = f"*Command:*\n```{command}```\n*Description:* {description}"
        else:
            message_text = f"🔔 Claude used: `{tool_name}`"
            # Pretty print the tool input
            detail_text = f"*Details:*\n```json\n{json.dumps(tool_input, indent=2)}```"
        
        # Send to Slack
        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            headers={
                'Authorization': f'Bearer {slack_token}',
                'Content-Type': 'application/json'
            },
            json={
                'channel': slack_channel,
                'text': message_text,
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"{message_text}\n{detail_text}"
                        }
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"Session: `{session_id[:8]}...`"
                            }
                        ]
                    }
                ]
            },
            timeout=5
        )
        
        # Always continue execution
        print('{"continue": true}')
        sys.exit(0)
        
    except Exception as e:
        # On any error, just continue
        print('{"continue": true}')
        sys.exit(0)


if __name__ == '__main__':
    main()