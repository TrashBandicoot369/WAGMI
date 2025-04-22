from telethon import TelegramClient
import asyncio

API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

client = TelegramClient("user_session1", API_ID, API_HASH)

# Add usernames to query
usernames = ["alphamaxxed", "reggyyy", "j1legend", "le_printoor"]

async def get_user_id(client, username):
    try:
        user = await client.get_entity(username)
        print(f"@{username} → {user.id}")
    except Exception as e:
        print(f"@{username} → ❌ {e}")

async def main():
    await client.start()
    for username in usernames:
        await get_user_id(client, username)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
