from telethon import TelegramClient
import os



async def download_dragndrop():
    async with TelegramClient('ericswan', os.environ['API_ID'], os.environ['API_HASH']) as client:
        last_msg = await client.get_messages('komodo_sync_bot', 1)
        await client.download_media(last_msg, '/root/new-binary.zip')



if '__main__' == '__name__':
    download_dragndrop()