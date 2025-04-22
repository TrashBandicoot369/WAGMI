from telethon import TelegramClient

API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

client = TelegramClient('user_session', API_ID, API_HASH)

async def get_username(user_id):
    try:
        user = await client.get_entity(user_id)
        username = user.username if user.username else "No username found"
        print(f"User ID: {user_id} | Username: @{username}")
    except Exception as e:
        print(f"Error for ID {user_id}: {e}")

# Your user IDs:
user_ids = [
    837563973, 7808944025, 1973324576, 1282880940,
    1634061759, 6849959621, 6859905194, 5692101176, 
    6763993595, 1665358865, 1772890464,
    5220299596, 1021989167, 7034010223, 7034413493, 
    451261430, 963718578, 5046008695, 7088866708, 
    581678251
]

with client:
    for user_id in user_ids:
        client.loop.run_until_complete(get_username(user_id))