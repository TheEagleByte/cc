#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

import json
import sys
import re
import os
import time
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests
except ImportError:
    requests = None

def is_dangerous_rm_command(command):
    """
    Comprehensive detection of dangerous rm commands.
    Matches various forms of rm -rf and similar destructive patterns.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = ' '.join(command.lower().split())
    
    # Pattern 1: Standard rm -rf variations
    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf, rm -fr, rm -Rf, etc.
        r'\brm\s+.*-[a-z]*f[a-z]*r',  # rm -fr variations
        r'\brm\s+--recursive\s+--force',  # rm --recursive --force
        r'\brm\s+--force\s+--recursive',  # rm --force --recursive
        r'\brm\s+-r\s+.*-f',  # rm -r ... -f
        r'\brm\s+-f\s+.*-r',  # rm -f ... -r
    ]
    
    # Check for dangerous patterns
    for pattern in patterns:
        if re.search(pattern, normalized):
            return True
    
    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    dangerous_paths = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~',           # Home directory
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards in general rm -rf context
        r'\.',          # Current directory
        r'\.\s*$',      # Current directory at end of command
    ]
    
    if re.search(r'\brm\s+.*-[a-z]*r', normalized):  # If rm has recursive flag
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True
    
    return False

def is_env_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access .env files containing sensitive data.
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')
            if '.env' in file_path and not file_path.endswith('.env.sample'):
                return True
        
        # Check bash commands for .env file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            # Pattern to detect .env file access (but allow .env.sample)
            env_patterns = [
                r'\b\.env\b(?!\.sample)',  # .env but not .env.sample
                r'cat\s+.*\.env\b(?!\.sample)',  # cat .env
                r'echo\s+.*>\s*\.env\b(?!\.sample)',  # echo > .env
                r'touch\s+.*\.env\b(?!\.sample)',  # touch .env
                r'cp\s+.*\.env\b(?!\.sample)',  # cp .env
                r'mv\s+.*\.env\b(?!\.sample)',  # mv .env
            ]
            
            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True
    
    return False

def requires_approval(tool_name):
    """
    Check if a tool requires Slack approval based on sensitivity.
    """
    # Tools that modify files require approval
    sensitive_tools = ['Write', 'Edit', 'MultiEdit']
    return tool_name in sensitive_tools

def send_slack_approval(input_data):
    """
    Send approval request to Slack and wait for response.
    Returns True if approved, False if denied.
    """
    if not requests:
        # Requests not available, auto-approve
        return True
    
    # Get Slack configuration
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL', 'claude-code')
    
    if not slack_token:
        # No Slack token, auto-approve
        return True
    
    try:
        session_id = input_data.get('session_id', 'unknown')
        tool_name = input_data.get('tool_name', 'unknown')
        tool_input = input_data.get('tool_input', {})
        
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
                detail_text = f"*File:* `{file_path}`\\n*Content Preview:*\\n```{content_preview}```"
            elif tool_name == 'Edit':
                old_string = tool_input.get('old_string', '')[:100]
                new_string = tool_input.get('new_string', '')[:100]
                detail_text = f"*File:* `{file_path}`\\n*Replace:*\\n```{old_string}```\\n*With:*\\n```{new_string}```"
            else:  # MultiEdit
                edits = tool_input.get('edits', [])
                detail_text = f"*File:* `{file_path}`\\n*Number of edits:* {len(edits)}"
        else:
            message_text = f"🚨 Approval Required: `{tool_name}`"
            detail_text = f"*Details:*\\n```json\\n{json.dumps(tool_input, indent=2)[:500]}```"
        
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
                            'text': f"{message_text}\\n{detail_text}"
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
                
                # Return True if approved, False otherwise
                return result.get('decision') == 'approve'
            
            time.sleep(1)
            elapsed += 1
        
        # Timeout - deny by default
        return False
        
    except Exception as e:
        # On error, be conservative and deny
        print(f"Error in Slack approval: {str(e)}", file=sys.stderr)
        return False

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Check for .env file access (blocks access to sensitive environment files)
        if is_env_file_access(tool_name, tool_input):
            print("BLOCKED: Access to .env files containing sensitive data is prohibited", file=sys.stderr)
            print("Use .env.sample for template files instead", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Check if tool requires approval
        if requires_approval(tool_name):
            if not send_slack_approval(input_data):
                print("BLOCKED: Operation denied via Slack approval", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Check for dangerous rm -rf commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            
            # Block rm -rf commands with comprehensive pattern matching
            if is_dangerous_rm_command(command):
                print("BLOCKED: Dangerous rm command detected and prevented", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Ensure log directory exists
        log_dir = Path.home() / '.claude' / 'hooks' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'pre_tool_use.json'
        
        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()