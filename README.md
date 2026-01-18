# Daily Founder Follow-Up Agent

An automated system that identifies meetings requiring follow-up emails and sends a daily Slack message with interactive "Done" buttons.

## Features
- **Daily Check**: Runs at 10am PT via GitHub Actions.
- **Agentic Logic**: Uses Claude 3.5 Sonnet + MCP (Clarify, Gmail, Calendar) to check meeting participants and sent emails.
- **Slack Integration**: Interactive Block Kit messages to manage follow-ups.
- **Persistent Storage**: Tracks completed items in SQLite to avoid duplicates.

## Setup

### 1. Slack App
1. Create a new Slack App in your workspace.
2. Enable **Interactivity & Shortcuts** and set the Request URL to your interaction handler endpoint (e.g., `https://your-app.railway.app/slack/interactive`).
3. Add `chat:write` and `chat:update` scopes.
4. Install the app and copy the `Bot User OAuth Token` and `Signing Secret`.

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in the values:
- `ANTHROPIC_API_KEY`: Your Anthropic API key.
- `SLACK_BOT_TOKEN`: Your Slack Bot token.
- `SLACK_SIGNING_SECRET`: Your Slack Signing Secret.
- `SLACK_CHANNEL_ID`: Your Slack user ID or channel ID for the DMs.

### 3. Deployment
- **Daily Check**: Handled by GitHub Actions. Add the environment variables as GitHub Secrets.
- **Interaction Handler**: Deploy `slack_handler.py` to a platform like Railway, Render, or Heroku.
  - Command: `gunicorn followup-agent.slack_handler:app --bind 0.0.0.0:$PORT`

## Local Development
1. `pip install -r requirements.txt`
2. `python -m followup_agent.check_followups` (Run check once)
3. `python -m followup_agent.slack_handler` (Start interaction server)

## Testing
`pytest tests/`
