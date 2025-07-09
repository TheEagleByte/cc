#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

"""
Slack approval hook for sensitive Claude Code operations.
Sends a message to Slack with approve/deny buttons and waits for user response.
Used for tools like Write, Edit, MultiEdit that modify files.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests
except ImportError:
    print('{"decision": "approve", "reason": "Requests library not available, auto-approving"}')
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
            # No Slack token, auto-approve
            print('{"decision": "approve", "reason": "No Slack token configured"}')
            sys.exit(0)
        
        # Create approval directory if it doesn't exist
        approval_dir = Path('/tmp/claude-approvals')
        approval_dir.mkdir(exist_ok=True)
        approval_file = approval_dir / f'{session_id}.json'
        
        # Remove any existing approval file
        if approval_file.exists():
            approval_file.unlink()
        
        # Format the message based on tool type
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', 'unknown')
            message_text = f"🚨 Approval Required: `{tool_name}`"
            
            if tool_name == 'Write':
                content_preview = tool_input.get('content', '')[:200]
                if len(tool_input.get('content', '')) > 200:
                    content_preview += '...'
                detail_text = f"*File:* `{file_path}`\n*Content Preview:*\n```{content_preview}```"
            elif tool_name == 'Edit':
                old_string = tool_input.get('old_string', '')[:100]
                new_string = tool_input.get('new_string', '')[:100]
                detail_text = f"*File:* `{file_path}`\n*Replace:*\n```{old_string}```\n*With:*\n```{new_string}```"
            else:  # MultiEdit
                edits = tool_input.get('edits', [])
                detail_text = f"*File:* `{file_path}`\n*Number of edits:* {len(edits)}"
        else:
            message_text = f"🚨 Approval Required: `{tool_name}`"
            detail_text = f"*Details:*\n```json\n{json.dumps(tool_input, indent=2)[:500]}```"
        
        # Prepare the value for button callbacks
        callback_value = json.dumps({
            'session_id': session_id,
            'tool_name': tool_name,
            'file_path': tool_input.get('file_path', 'N/A')
        })
        
        # Send approval request to Slack
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
                        'type': 'actions',
                        'elements': [
                            {
                                'type': 'button',
                                'text': {
                                    'type': 'plain_text',
                                    'text': '✅ Approve'
                                },
                                'style': 'primary',
                                'value': callback_value,
                                'action_id': 'approve_command'
                            },
                            {
                                'type': 'button',
                                'text': {
                                    'type': 'plain_text',
                                    'text': '❌ Deny'
                                },
                                'style': 'danger',
                                'value': callback_value,
                                'action_id': 'deny_command'
                            }
                        ]
                    }
                ]
            },
            timeout=5
        )
        
        # Wait for approval file (up to 60 seconds)
        timeout = 60
        elapsed = 0
        
        while elapsed < timeout:
            if approval_file.exists():
                # Read the approval decision
                with open(approval_file, 'r') as f:
                    result = json.load(f)
                
                # Clean up the file
                approval_file.unlink()
                
                # Output the result
                print(json.dumps(result))
                sys.exit(0)
            
            time.sleep(1)
            elapsed += 1
        
        # Timeout - block the operation
        result = {
            'decision': 'block',
            'reason': 'Timeout waiting for Slack approval (60 seconds)'
        }
        print(json.dumps(result))
        sys.exit(2)
        
    except Exception as e:
        # On error, be conservative and block
        result = {
            'decision': 'block',
            'reason': f'Error in approval hook: {str(e)}'
        }
        print(json.dumps(result))
        sys.exit(2)


if __name__ == '__main__':
    main()