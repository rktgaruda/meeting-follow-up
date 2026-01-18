import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Slack Configuration
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# Business Logic
USER_EMAIL = os.getenv("USER_EMAIL", "rishi@garuda.vc")
INTERNAL_EMAILS = [e.strip() for e in os.getenv("INTERNAL_EMAILS", "").split(",") if e.strip()]
MEETING_TYPES = [t.strip() for t in os.getenv("MEETING_TYPES", "").split(",") if t.strip()]
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "7"))

# Storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///followups.db")
if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    DB_PATH = "followups.db"
