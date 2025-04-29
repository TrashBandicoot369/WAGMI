from telethon import TelegramClient
import asyncio

# API credentials from qwant3.py
API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

# The invite links
INVITE_LINKS = [
    "https://t.me/+789RPo-iGzljYzBh",  # ShotCollaz invite link
    "https://t.me/+GCPURpJGsa82ZGUx",  # WAGMI invite link
    "https://t.me/HighVolumeBordga",  # SOL High Volume
]

async def main():
    # Create a client
    print("Starting client...")
    client = TelegramClient("id_finder_session", API_ID, API_HASH)
    await client.start()
    print("Client started. Getting entities...")
    
    # Try to resolve each invite link
    for link in INVITE_LINKS:
        try:
            # Attempt to join or get the group
            print(f"Trying to resolve: {link}")
            entity = await client.get_entity(link)
            print(f"Success! Group ID: {entity.id} ({entity.title})")
        except Exception as e:
            print(f"Error with {link}: {e}")
    
    await client.disconnect()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main()) 