from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import ChannelPrivateError
import firebase_admin
from firebase_admin import credentials, firestore
import re
import asyncio
import requests
from bs4 import BeautifulSoup
from lib.tokenResolver import resolve_token_symbol

# --- Firebase Setup ---
cred = credentials.Certificate("wagmi-crypto-calls-firebase-adminsdk-fbsvc-53372d3ca7.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
calls_ref = db.collection("calls")

# --- Dexscreener Symbol Lookup ---
def get_token_symbol(contract: str):
    try:
        url = f"https://dexscreener.com/solana/{contract}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            print("\n📄 HTML preview:\n", soup.prettify()[:1000])
            ticker = soup.find("span", class_="text-lg font-bold")
            if ticker:
                symbol = ticker.text.replace("$", "").strip().upper()
                print(f"✅ Ticker found: {symbol}")
                return symbol
            else:
                print("⚠️ Ticker not found in HTML.")
        else:
            print(f"⚠️ Dexscreener responded with status: {res.status_code}")
    except Exception as e:
        print(f"❌ Exception during Dexscreener scrape: {e}")
    return "UNKNOWN"

# --- Telegram Setup ---
API_ID_1 = 29312830
API_HASH_1 = "24622c388a689db6cf871903fdca8c1c"
API_ID_2 = 26108909
API_HASH_2 = "3cb55b9919cee50e576611641283ec5a"

SOURCE_GROUPS_CLIENT1 = [-1002048135645, -1002238854475, 2179220327]
SOURCE_GROUPS_CLIENT2 = [-1001758236818]
DESTINATION_GROUPS = [-1002416386782, -1002651955296]

USER_MAPPING = {
    837563973: "Unknown",
    7808944025: "Unknown",
    1973324576: "Unknown",
    1282880940: "Unknown",
    1634061759: "Unknown",
    6849959621: "Unknown",
    5692101176: "Unknown",
    6763993595: "Unknown",
    1665358865: "wabibi",
    1772890464: "octosea",
    1021989167: "EntityNotFound",
    7034010223: "mr_moonrunitup",
    7034413493: "robertnfa",
    963718578: "ohcharlie",
    5046008695: "edgrudskiy",
    7088866708: "Helpermicin",
    581678251: "reggyyy"
}

SHOT_CALLERS = [5337215623, 7137640996, 7538811744, 963718578, 5220299596, 6047628843, 451261430]
CALLERS = [uid for uid in USER_MAPPING if uid not in SHOT_CALLERS]

client1 = TelegramClient("user_session1", API_ID_1, API_HASH_1)
client2 = TelegramClient("user_session2", API_ID_2, API_HASH_2)

def create_handler(source_groups):
    async def handler(event):
        try:
            chat = await event.get_chat()
            sender = await event.get_sender()
            if sender.id not in CALLERS + SHOT_CALLERS:
                return

            username = USER_MAPPING.get(sender.id, sender.username or "Unknown")
            username_display = f"@{username}" if username != "Unknown" else "Unknown"

            print(f"\n{'='*20} NEW MESSAGE {'='*20}")
            print(f"Group: {chat.title} | ID: {chat.id}")
            print(f"User: {username_display} (ID: {sender.id})")
            print(f"Message: {event.message.text}")
            print(f"{'='*50}\n")

            ca_match = re.search(r"(0x[a-fA-F0-9]{40}|[A-Za-z0-9]{25,44})", event.message.text)
            if ca_match:
                contract = ca_match.group(1)
                token = await resolve_token_symbol(contract)

                payload = {
                    "token": token,
                    "dexurl": f"https://dexscreener.com/solana/{contract}",
                    "timestamp": firestore.SERVER_TIMESTAMP
                }

                print(f"📦 Pushing to Firestore: {payload}")
                try:
                    doc_ref = calls_ref.add(payload)
                    print(f"🔥 Firestore write succeeded. Document ref: {doc_ref}")
                except Exception as e:
                    print(f"❌ Firestore write FAILED: {type(e).__name__} - {e}")

                header = "🧠💥 BIG BRAIN CALL 💥🧠" if sender.id in SHOT_CALLERS else "🚨 ALERT 🚨"
                msg = (
                    f"{header}\n"
                    f"Group: {chat.title}\n"
                    f"User: {username_display} (ID: {sender.id})\n"
                    f"Message:\n{event.message.text}"
                )

                for group_id in DESTINATION_GROUPS:
                    if group_id == -1002651955296 and sender.id not in SHOT_CALLERS:
                        continue
                    try:
                        await event.client.send_message(group_id, msg)
                        print(f"✅ Forwarded to {group_id}")
                    except ChannelPrivateError:
                        try:
                            await event.client(JoinChannelRequest(group_id))
                            await event.client.send_message(group_id, msg)
                        except Exception as e:
                            print(f"❌ Failed to join/send to {group_id}: {e}")
                    except Exception as e:
                        print(f"❌ Send error: {e}")
        except Exception as e:
            print(f"❌ Handler error: {e}")
    return handler

client1.add_event_handler(
    create_handler(SOURCE_GROUPS_CLIENT1),
    events.NewMessage(chats=SOURCE_GROUPS_CLIENT1, from_users=CALLERS + SHOT_CALLERS)
)

client2.add_event_handler(
    create_handler(SOURCE_GROUPS_CLIENT2),
    events.NewMessage(chats=SOURCE_GROUPS_CLIENT2, from_users=CALLERS + SHOT_CALLERS)
)

async def main():
    await client1.start()
    await client2.start()
    print("Monitoring active. Press Ctrl+C to stop.")
    await asyncio.gather(client1.run_until_disconnected(), client2.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
