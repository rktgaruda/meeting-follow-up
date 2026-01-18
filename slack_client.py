from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
import logging

class SlackClient:
    def __init__(self, token: str = SLACK_BOT_TOKEN):
        self.client = WebClient(token=token)
        self.channel_id = SLACK_CHANNEL_ID

    def post_message(self, blocks: list, text: str = "Meeting Follow-up Reminder"):
        """Sends a Block Kit message to Slack."""
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=text
            )
            return response["ts"]
        except SlackApiError as e:
            logging.error(f"Error posting message to Slack: {e}")
            return None

    def update_message(self, ts: str, blocks: list, text: str = "Meeting Follow-up Reminder"):
        """Updates an existing Block Kit message."""
        try:
            self.client.chat_update(
                channel=self.channel_id,
                ts=ts,
                blocks=blocks,
                text=text
            )
            return True
        except SlackApiError as e:
            logging.error(f"Error updating Slack message: {e}")
            return False

    def format_followup_blocks(self, followups: list):
        """Formats the follow-up list into Slack Block Kit."""
        if not followups:
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✨ *All clear!* No meeting follow-ups needed today. Great job staying on top of things!"
                    }
                }
            ]

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "👋 *Good morning, Rishi!* Here are the meetings that might need a follow-up email:"
                }
            },
            {"type": "divider"}
        ]

        for item in followups:
            meeting_id = item.get("meeting_id")
            contact = item.get("contact_name", "Unknown")
            company = item.get("company", "Unknown")
            date = item.get("meeting_date", "Unknown")
            m_type = item.get("meeting_type", "Unknown")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"* {contact}* ({company})\n_{date}_ | {m_type}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Done ✓",
                        "emoji": True
                    },
                    "action_id": "mark_done",
                    "value": f"meeting_id:{meeting_id}"
                }
            })

        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Items marked as 'Done' will be removed from this list."
                }
            ]
        })

        return blocks
