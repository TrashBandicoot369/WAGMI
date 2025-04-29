import asyncio
from telethon.sync import TelegramClient
from telethon import functions, types

# Telegram API Config
API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

# Session file must exist in your project root
SESSION_FILE = 'user_session1'  # This should already be authenticated

async def list_chats():
    """List all available chats and channels"""
    print("🔍 Listing available Telegram chats and channels...")
    
    # Start Telegram client
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        print("✅ Connected to Telegram using existing session")
        
        # Make sure we're properly connected
        me = await client.get_me()
        print(f"✅ Authenticated as: {me.username or me.phone}")
        
        # Get dialogs (chats, channels, users you've talked with)
        print("\n📋 Available chats and channels:")
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            
            # Check if it's a channel or group
            if isinstance(entity, types.Channel):
                channel_type = "Channel" if entity.broadcast else "Group"
                print(f"ID: {entity.id}, Type: {channel_type}, Name: {dialog.name}")
                try:
                    # Try to check permissions
                    permissions = await client(functions.channels.GetParticipantRequest(
                        channel=entity,
                        participant=me.id
                    ))
                    can_post = "Yes" if hasattr(permissions.participant, 'admin_rights') else "No (Member only)"
                    print(f"   Can post: {can_post}")
                except Exception as e:
                    print(f"   Permission check error: {str(e)}")
            
            # Check if it's a regular chat
            elif isinstance(entity, types.Chat):
                print(f"ID: {entity.id}, Type: Chat, Name: {dialog.name}")
                print(f"   Can post: Yes (Regular chat)")
            
            # Limit to 10 results for cleaner output
            if dialog.id >= 10:
                break
    
    except Exception as e:
        print(f"❌ Error during chat listing: {e}")
    
    finally:
        # Disconnect client
        await client.disconnect()
        print("\n👋 Disconnected from Telegram")
        
    print("\n📝 Instructions:")
    print("1. Note down the ID of a channel or group where you have posting permission")
    print("2. Update the CHAT_IDS in telegram_forward.py with this ID")
    print("3. Run the forwarding test again")

if __name__ == "__main__":
    asyncio.run(list_chats()) 