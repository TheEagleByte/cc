#!/usr/bin/env node
/**
 * Slack bot server for handling Claude Code approval workflows.
 * This bot listens for button interactions and writes approval decisions.
 */

const { App } = require('@slack/bolt');
const fs = require('fs').promises;
const path = require('path');

// Load environment variables
require('dotenv').config();

// Initialize Slack app
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  socketMode: true,
  appToken: process.env.SLACK_APP_TOKEN,
});

// Ensure approval directory exists
const APPROVAL_DIR = '/tmp/claude-approvals';
fs.mkdir(APPROVAL_DIR, { recursive: true }).catch(console.error);

// Handle approve button clicks
app.action('approve_command', async ({ body, ack, client }) => {
  await ack();
  
  try {
    // Parse the button value
    const { session_id, tool_name, file_path } = JSON.parse(body.actions[0].value);
    
    // Write approval decision
    const result = {
      decision: 'approve',
      reason: `User ${body.user.name} approved`,
      timestamp: new Date().toISOString(),
      user: body.user.name,
      tool_name,
      file_path
    };
    
    await fs.writeFile(
      path.join(APPROVAL_DIR, `${session_id}.json`),
      JSON.stringify(result, null, 2)
    );
    
    // Update the Slack message
    await client.chat.update({
      channel: body.channel.id,
      ts: body.message.ts,
      text: `✅ Approved by ${body.user.name}`,
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `✅ *Approved by ${body.user.name}*\n\`${tool_name}\` on \`${file_path}\`\n_${new Date().toLocaleString()}_`
          }
        }
      ]
    });
    
    console.log(`Approved: ${tool_name} on ${file_path} by ${body.user.name}`);
    
  } catch (error) {
    console.error('Error handling approval:', error);
    
    // Try to update message with error
    try {
      await client.chat.update({
        channel: body.channel.id,
        ts: body.message.ts,
        text: `❌ Error processing approval: ${error.message}`
      });
    } catch (updateError) {
      console.error('Failed to update message:', updateError);
    }
  }
});

// Handle deny button clicks
app.action('deny_command', async ({ body, ack, client }) => {
  await ack();
  
  try {
    // Parse the button value
    const { session_id, tool_name, file_path } = JSON.parse(body.actions[0].value);
    
    // Write denial decision
    const result = {
      decision: 'deny',
      reason: `User ${body.user.name} denied`,
      timestamp: new Date().toISOString(),
      user: body.user.name,
      tool_name,
      file_path
    };
    
    await fs.writeFile(
      path.join(APPROVAL_DIR, `${session_id}.json`),
      JSON.stringify(result, null, 2)
    );
    
    // Update the Slack message
    await client.chat.update({
      channel: body.channel.id,
      ts: body.message.ts,
      text: `❌ Denied by ${body.user.name}`,
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `❌ *Denied by ${body.user.name}*\n\`${tool_name}\` on \`${file_path}\`\n_${new Date().toLocaleString()}_`
          }
        }
      ]
    });
    
    console.log(`Denied: ${tool_name} on ${file_path} by ${body.user.name}`);
    
  } catch (error) {
    console.error('Error handling denial:', error);
    
    // Try to update message with error
    try {
      await client.chat.update({
        channel: body.channel.id,
        ts: body.message.ts,
        text: `❌ Error processing denial: ${error.message}`
      });
    } catch (updateError) {
      console.error('Failed to update message:', updateError);
    }
  }
});

// Start the app
(async () => {
  try {
    await app.start();
    console.log('⚡️ Claude Code Slack bot is running!');
    console.log(`📁 Approval directory: ${APPROVAL_DIR}`);
    console.log('👀 Listening for approval requests...');
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\n👋 Shutting down bot...');
      await app.stop();
      process.exit(0);
    });
    
  } catch (error) {
    console.error('Failed to start bot:', error);
    process.exit(1);
  }
})();