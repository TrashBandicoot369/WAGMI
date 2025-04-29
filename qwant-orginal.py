from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import ChannelPrivateError
import re
import asyncio

# Account configurations
API_ID_1 = 29312830
API_HASH_1 = "24622c388a689db6cf871903fdca8c1c"
SOURCE_GROUPS_CLIENT1 = [
    -1002048135645,  # RUF
    -1002238854475,  # PBC
    2179220327       # SNIPERUNI
]

API_ID_2 = 26108909
API_HASH_2 = "3cb55b9919cee50e576611641283ec5a"
SOURCE_GROUPS_CLIENT2 = [
    -1001758236818,  # The Sauna
]

# USER MAPPING WITH KNOWN USERNAMES
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

# Updated caller lists
SHOT_CALLERS = [
    5337215623,  # bizonacci
    7137640996,  # J1Legend
    7538811744,  # Le_Printoor
    963718578,   # ohcharlie
    5220299596,  # alphameo
    6047628843,  # amitysol
    451261430,   # sonder_crypto
    
]

CALLERS = [uid for uid in USER_MAPPING.keys() if uid not in SHOT_CALLERS]

DESTINATION_GROUPS = [
    -1002416386782,  # Original Shot Collaz
    -1002651955296   # WAGMI (only shot callers)
]

# Create client instances
client1 = TelegramClient('user_session1', API_ID_1, API_HASH_1)
client2 = TelegramClient('user_session2', API_ID_2, API_HASH_2)

# Event handler factory
def create_handler(source_groups):
    async def handler(event):
        try:
            chat = await event.get_chat()
            sender = await event.get_sender()
            
            # Skip non-monitored users
            if sender.id not in CALLERS + SHOT_CALLERS:
                return

            # Get username from mapping or fallback
            username = USER_MAPPING.get(sender.id, sender.username or "Unknown")
            username_display = f"@{username}" if username != "Unknown" else "Unknown"

            # Log message details
            print(f"\n{'='*20} NEW MESSAGE {'='*20}")
            print(f"Group: {chat.title} | ID: {chat.id}")
            print(f"User: {username_display} (ID: {sender.id})")
            print(f"Message: {event.message.text}")
            print(f"{'='*50}\n")

            # Check for regex pattern
            if re.search(r'\b[A-Za-z0-9]{32,50}\b', event.message.text):
                alert_header = "🧠💥 BIG BRAIN CALL 💥🧠" if sender.id in SHOT_CALLERS else "🚨 ALERT 🚨"
                
                formatted = (
                    f"{alert_header}\n"
                    f"Group: {chat.title}\n"
                    f"User: {username_display} (ID: {sender.id})\n"
                    f"Message:\n{event.message.text}"
                )

                for group_id in DESTINATION_GROUPS:
                    try:
                        # Apply special rule for WAGMI group
                        if group_id == -1002651955296 and sender.id not in SHOT_CALLERS:
                            continue
                        
                        # Try sending message
                        await event.client.send_message(group_id, formatted)
                        print(f"✅ Forwarded to {group_id}")

                    except ChannelPrivateError:
                        print(f"⚠️ Not in group {group_id}, attempting to join...")
                        try:
                            await event.client(JoinChannelRequest(group_id))
                            print(f"✅ Joined {group_id}")
                            # Retry sending after joining
                            await event.client.send_message(group_id, formatted)
                        except Exception as e:
                            print(f"❌ Failed to join {group_id}: {type(e).__name__}")

                    except Exception as e:
                        print(f"❌ Failed to send to {group_id}: {type(e).__name__}")

        except Exception as e:
            print(f"❌ Critical error: {type(e).__name__}")

    return handler

# Set up handlers
client1.add_event_handler(
    create_handler(SOURCE_GROUPS_CLIENT1),
    events.NewMessage(
        chats=SOURCE_GROUPS_CLIENT1,
        from_users=CALLERS + SHOT_CALLERS
    )
)

client2.add_event_handler(
    create_handler(SOURCE_GROUPS_CLIENT2),
    events.NewMessage(
        chats=SOURCE_GROUPS_CLIENT2,
        from_users=CALLERS + SHOT_CALLERS
    )
)

async def main():
    await client1.start()
    await client2.start()
    print(f"Client 1 monitoring: {SOURCE_GROUPS_CLIENT1}")
    print(f"Client 2 monitoring: {SOURCE_GROUPS_CLIENT2}")
    print("Monitoring active. Press Ctrl+C to stop.")
    await asyncio.gather(
        client1.run_until_disconnected(),
        client2.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())