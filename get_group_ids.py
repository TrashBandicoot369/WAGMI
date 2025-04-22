from telethon import TelegramClient
from telethon.errors import UsernameInvalidError, InviteHashInvalidError

API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

client = TelegramClient('user_session', API_ID, API_HASH)

async def get_group_id(identifier):
    try:
        # Handle invite links (e.g., "111")
        if "t.me" in identifier:
            invite_hash = identifier.split("/")[-1]
            group = await client.get_entity(invite_hash)
        # Handle usernames (e.g., "The Sauna : Crosschain Bangers")
        else:
            group = await client.get_entity(identifier)
        
        print(f"✅ Group: {group.title} | ID: {group.id}")

    except UsernameInvalidError:
        print(f"❌ Invalid username/invite link: {identifier}")
    except InviteHashInvalidError:
        print(f"❌ Invalid/expired invite link: {identifier}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {e}")

# Replace with your group's actual username or invite link
groups = ["WAGMI", "https://t.me/+GCPURpJGsa82ZGUx"]

with client:
    for group in groups:
        client.loop.run_until_complete(get_group_id(group))