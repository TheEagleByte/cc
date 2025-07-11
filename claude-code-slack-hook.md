# How Claude Code Hook with Slack Helps Me Build My Dreams — While Raising a Kid and Working Full-Time | by Zero Code Startup | Jul, 2025 | Medium

I’m a **full-time software engineer** with 15 years of experience, currently working at a Big Tech company in Silicon Valley. Like many others, I’m also **a parent for two toodlers**. Between a demanding job and raising a young child, time is the one thing I never have enough of. Yet, I have dreams — building tools, shipping products, composing music, and launching startups.

![](https://miro.medium.com/v2/resize:fit:700/1*eIV4-pQWKGg1AmZkUKON8g.png)

So when Claude Code launched with [agentic coding capabilities](https://docs.anthropic.com/en/docs/claude-code), it felt like hiring two junior developers who work 24/7. Unlike other AI tools like WindSurf or Cursor AI, Claude is fast, responsive, and shockingly capable in its agentic mode. It made it finally possible to turn my napkin sketches into working code, often from just a few prompts.

But there was a catch.

# The Bottleneck: Approvals

While Claude Code could do wonders, it often stopped mid-task due to Bash command permissions or file edits that required human approval. Sometimes it would wait for hours while I was off putting my daughter to bed or in a meeting. Other times, it would get stuck simply because it needed my confirmation to continue editing a config file.

Yes, you could pre-whitelist certain commands. But when you’re letting an agent explore unfamiliar territory — especially anything affecting the file system — you don’t want it to run unchecked.

That’s when I discovered [Claude Hook](https://docs.anthropic.com/en/docs/claude-code/ide-integrations). This interface lets you intercept tool execution via a custom script. I immediately thought:

> _“Why not send these approval requests to Slack, where I can tap ‘Approve’ on my Apple Watch or phone — without even opening the editor?”_

And that’s exactly what I built.

# Solution Architecture: Claude Hook + Slack Approval System

Here’s what I built in just a couple of sessions using Claude Code itself:

## System Flow

1.  Claude tries to run tool
2.  Hook intercepts
3.  Slack message sent
4.  I approve/deny on phone/watch
5.  Claude continues or stops

## Three Key Components

1.  Claude Hook scripts (PreToolUse)
2.  Slack bot with interactive buttons
3.  Temporary file-based approval queue

# Implementation: Step-by-Step

## 1\. Notification-Only Hook (No Approval Required)

This version simply sends a Slack message when Claude uses safe tools like Grep, LS, or Bash.

#!/bin/bash  
\# ~/.claude/hooks/slack-notify-only.sh  
  
read -r input  
session\_id=$(echo "$input" | jq -r '.session\_id')  
tool\_name=$(echo "$input" | jq -r '.tool\_name')  
command\=$(echo "$input" | jq -r '.tool\_input.command')  
curl -s -X POST "https://slack.com/api/chat.postMessage" \\  
  -H "Authorization: Bearer $SLACK\_BOT\_TOKEN" \\  
  -H 'Content-type: application/json' \\  
  -d "$(jq -n \\  
    --arg channel "claude-code" \\  
    --arg text "🔔 Claude ran a safe command" \\  
    --arg tool "$tool\_name" \\  
    --arg cmd "$command" \\  
    '{  
      channel: $channel,  
      text: $text,  
      blocks: \[  
        {  
          type: "section",  
          text: { type: "mrkdwn", text: "\*Tool:\* \\($tool)\\n\*Command:\*\\n\`\`\`\\($cmd)\`\`\`" }  
        }  
      \]  
    }')" > /dev/null  
echo '{"continue": true}'

## 2\. Approval-Waiting Hook (Sensitive Tools)

This one waits for your Slack approval before proceeding.

#!/bin/bash  
\# ~/.claude/hooks/slack-wait-approval.sh  
  
read -r input  
session\_id=$(echo "$input" | jq -r '.session\_id')  
command\=$(echo "$input" | jq -r '.tool\_input.command')  
value\_json=$(jq -n \\  
  --arg session\_id "$session\_id" \\  
  --arg command "$command" \\  
  '{ session\_id: $session\_id, command: $command }' | jq -c)  
curl -s -X POST "https://slack.com/api/chat.postMessage" \\  
  -H "Authorization: Bearer $SLACK\_BOT\_TOKEN" \\  
  -H 'Content-type: application/json' \\  
  -d "$(jq -n \\  
    --arg channel "claude-code" \\  
    --arg text "🚨 Command Approval Required" \\  
    --arg cmd "$command" \\  
    --arg value "$value\_json" \\  
    '{  
      channel: $channel,  
      text: $text,  
      blocks: \[  
        {  
          type: "section",  
          text: { type: "mrkdwn", text: "\*Command:\*\\n\`\`\`\\($cmd)\`\`\`" }  
        },  
        {  
          type: "actions",  
          elements: \[  
            {  
              type: "button",  
              text: { type: "plain\_text", text: "✅ Approve" },  
              style: "primary",  
              value: $value,  
              action\_id: "approve\_command"  
            },  
            {  
              type: "button",  
              text: { type: "plain\_text", text: "❌ Deny" },  
              style: "danger",  
              value: $value,  
              action\_id: "deny\_command"  
            }  
          \]  
        }  
      \]  
    }')"  
\# Wait for file approval  
approval\_file="/tmp/claude-approvals/$session\_id.json"  
timeout\=60  
elapsed=0  
while \[ ! -f "$approval\_file" \] && \[ $elapsed -lt $timeout \]; do  
  sleep 1  
  elapsed=$((elapsed + 1))  
done  
if \[ -f "$approval\_file" \]; then  
  cat "$approval\_file"  
  rm "$approval\_file"  
else  
  echo '{"continue": false, "stopReason": "Slack timeout"}'  
  exit 2  
fi

## 3.settings.json Configuration for Claude Code

{  
  "hooks": {  
    "PreToolUse": \[  
      {  
        "matcher": "^(Read|Write|Edit|MultiEdit)$",  
        "hooks": \[  
          { "type": "command", "command": "~/.claude/hooks/slack-wait-approval.sh" }  
        \]  
      },  
      {  
        "matcher": "^(Bash|Grep|Glob|LS)$",  
        "hooks": \[  
          { "type": "command", "command": "~/.claude/hooks/slack-notify-only.sh" }  
        \]  
      }  
    \]  
  }  
}

## 4\. Slack Bot to Handle Button Clicks

Here’s a simple Node.js listener:

app.action(/approve\_command|deny\_command/, async ({ body, ack }) => {  
  await ack();  
  const { session\_id, command } = JSON.parse(body.actions\[0\].value);  
  const decision = body.actions\[0\].action\_id === "approve\_command" ? "approve" : "deny";  
  
  const result = {  
      decision,  
      reason: \`User ${decision}d\`,  
      timestamp: new Date().toISOString()  
    };  
    await fs.writeFile(\`/tmp/claude-approvals/${session\_id}.json\`, JSON.stringify(result));  
});

# Real-World Impact: Approving Commands from My Apple Watch

Now I get notified instantly on my phone or watch when Claude tries to edit something sensitive. I just tap ✅ and Claude continues working — while I go back to parenting or focus on my actual work.

![](https://miro.medium.com/v2/resize:fit:700/1*fxPmCOl4Ue4lrVSPCjKCgA.png)

This small integration made Claude go from “neat assistant” to “co-pilot that runs while I sleep.”

# What’s Next?

In my next post, I’ll walk through how I manage **session-specific command routing** inside VS Code when using Claude extensions — so you can control multiple sessions without conflict.

And eventually, I’ll integrate this with my startup’s productivity tools for AI-powered solopreneurs.

If you’re a busy parent, engineer, or creator trying to squeeze time out of a chaotic day, don’t sleep on Claude Hooks.

Combined with Slack, it becomes your invisible teammate — one that waits for your signal before moving forward.

**What about you? Have you tried building guardrails around your AI agent? Drop a comment and let me know.**