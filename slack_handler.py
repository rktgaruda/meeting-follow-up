import hmac
import hashlib
import time
import json
import logging
from flask import Flask, request, jsonify
from config import SLACK_SIGNING_SECRET
from storage import Storage
from slack_client import SlackClient

app = Flask(__name__)
storage = Storage()
slack = SlackClient()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_slack_signature(request):
    """Verifies that the request actually came from Slack."""
    timestamp = request.headers.get('X-Slack-Request-Timestamp')
    signature = request.headers.get('X-Slack-Signature')
    
    if not timestamp or not signature:
        return False
        
    # Prevent replay attacks
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
        
    sig_basestring = f"v0:{timestamp}:{request.get_data().decode('utf-8')}".encode('utf-8')
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)

@app.route("/slack/interactive", methods=["POST"])
def interactive():
    if not verify_slack_signature(request):
        return jsonify({"error": "invalid_signature"}), 403

    payload = json.loads(request.form["payload"])
    
    if payload["type"] == "block_actions":
        for action in payload["actions"]:
            if action["action_id"] == "mark_done":
                # Value is "meeting_id:XXXXX"
                value = action["value"]
                meeting_id = value.replace("meeting_id:", "")
                
                logging.info(f"Marking meeting {meeting_id} as done.")
                storage.mark_complete(meeting_id, method="slack_button")
                
                # Update the original message
                message_ts = payload["container"]["message_ts"]
                blocks = payload["message"]["blocks"]
                
                # Filter out the item that was just marked done
                new_blocks = []
                for block in blocks:
                    # Check if this block is a section with the button we just clicked
                    if block.get("type") == "section" and block.get("accessory") and \
                       block["accessory"].get("value") == value:
                        continue # Skip this block
                    new_blocks.append(block)
                
                # If only header/divider/footer remains, show "all clear"
                if len([b for b in new_blocks if b.get("type") == "section"]) == 1:
                    new_blocks = slack.format_followup_blocks([])
                
                slack.update_message(message_ts, new_blocks)
                
    return jsonify({"status": "ok"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
