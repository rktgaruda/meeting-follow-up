import json
import logging
import datetime
import anthropic
from config import (
    ANTHROPIC_API_KEY, USER_EMAIL, INTERNAL_EMAILS, 
    MEETING_TYPES, LOOKBACK_DAYS
)
from slack_client import SlackClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FollowUpAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.slack = SlackClient()

    def construct_prompt(self) -> str:
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=LOOKBACK_DAYS)
        
        prompt = f"""
You are a Founders Assistant agent. Your goal is to identify meetings that require a follow-up email.

**Context:**
- User Email: {USER_EMAIL}
- Internal Team Emails (Exclude): {", ".join(INTERNAL_EMAILS)}
- Meeting Types to Include: {", ".join(MEETING_TYPES)}
- Date Range: {seven_days_ago} to {today}

**Your Task:**
1. Call `Clarify:get-current-user` to confirm the user context.
2. Call `Clarify:query-data` to find meetings where {USER_EMAIL} was a participant within the date range.
3. Filter the results:
   - Exclude internal meetings (where all participants are from the internal team list).
   - Exclude personal appointments or panels.
   - ONLY include meetings matching the Types to Include.
4. For each remaining meeting, check if a follow-up has been sent:
   - Identify external participant emails.
   - Use `search_gmail_messages` to look for sent emails FROM {USER_EMAIL} TO those external participants since the meeting date.
5. If NO sent email is found for a meeting, it needs a follow-up.

**Output Format:**
Return ONLY a valid JSON object. No preamble, no markdown formatting (unless necessary for the JSON string).
JSON Structure:
{{
  "followups": [
    {{
      "meeting_id": "...",
      "contact_name": "...",
      "company": "...",
      "meeting_date": "...",
      "meeting_type": "...",
      "participant_emails": ["..."]
    }}
  ]
}}
If no follow-ups are needed, return: {{"followups": []}}
"""
        return prompt

    def run_daily_check(self):
        logging.info("Starting daily follow-up check...")
        prompt = self.construct_prompt()

        try:
            # Note: We are using Claude 3.5 Sonnet which has access to MCP tools in the user's environment.
            # In this script execution context, we expect the tools to be available via the API.
            response = self.client.messages.create(
                # Trying the most stable legacy version or the 'latest' string
                model="claude-3-5-sonnet-20240620", 
                max_tokens=2048,
                system="You are a meticulous founders assistant with access to Clarify, Gmail, and Google Calendar tools.",
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            logging.info(f"Received response from Claude: {response_text}")

            # Try to parse JSON from response
            try:
                # Handle cases where Claude might wrap JSON in backticks
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text.strip()
                
                data = json.loads(json_str)
                followups = data.get("followups", [])

                logging.info(f"Found {len(followups)} meetings needing follow-up.")
                
                blocks = self.slack.format_followup_blocks(followups)
                self.slack.post_message(blocks)

            except (json.JSONDecodeError, IndexError) as e:
                logging.error(f"Failed to parse Claude's JSON response: {e}")
                self.slack.post_message([{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "⚠️ *Error parsing follow-up list.* Claude's response didn't contain valid JSON. Please check logs."
                    }
                }])

        except Exception as e:
            logging.error(f"Error calling Anthropic API: {e}")
            self.slack.post_message([{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ *Failed to check follow-ups.* The agent encountered an error while communicating with Claude."
                }
            }])

if __name__ == "__main__":
    agent = FollowUpAgent()
    agent.run_daily_check()
