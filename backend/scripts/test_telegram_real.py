"""
Test script to send a REAL Telegram message using values from .env.
"""
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Load .env from root
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(root_dir, ".env")
load_dotenv(env_path)

async def test_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print(f"Token: {token[:5]}... (len={len(token) if token else 0})")
    print(f"Chat ID: {chat_id}")

    if not token or not chat_id:
        print("❌ Missing token or chat_id in .env")
        return

    base_url = f"https://api.telegram.org/bot{token}"
    
    print("\nSending test message...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. Test getMe
            resp = await client.get(f"{base_url}/getMe")
            if resp.status_code != 200:
                print(f"❌ getMe failed: {resp.text}")
                return
            
            bot_info = resp.json()
            print(f"✅ Bot found: @{bot_info['result']['username']}")

            # 2. Test sendMessage
            msg = "🔔 *Test Message from VintedScanner*\n\nIf you see this, configuration is correct!"
            
            resp = await client.post(
                f"{base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": msg,
                    "parse_mode": "Markdown"
                }
            )
            
            if resp.status_code == 200:
                print("✅ Message sent successfully!")
            else:
                print(f"❌ Message failed: {resp.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram())
