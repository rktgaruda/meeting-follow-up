import anthropic
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def list_models():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in environment.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    try:
        # Note: As of late 2025/2026, the list models endpoint might be different 
        # but usually it's client.models.list()
        print("Checking available models...")
        # Since I'm not sure of the exact 2026 method, I'll try the common ones
        models = client.models.list()
        print("\n✅ Available Models:")
        for model in models:
            print(f"- {model.id}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        print("\nTrying legacy check...")
        # Fallback to a simple message with a very old model to see if it works
        try:
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}]
            )
            print("✅ Claude 3 Haiku (legacy) is accessible.")
        except Exception as e2:
            print(f"❌ Legacy check failed too: {e2}")

if __name__ == "__main__":
    list_models()
