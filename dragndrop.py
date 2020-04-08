from telethon import TelegramClient
import os
import time

#this function is deactivated for now. issue #6
client = TelegramClient('binary-download', os.environ['API_ID'], os.environ['API_HASH'])


async def download_binaries():
    last_msg = await client.get_messages('komodo_sync_bot', 2)
    last_msg = last_msg[1]
    if last_msg.document:
        await last_msg.download_media('/root/new-binaries.zip')


with client:
    client.loop.run_until_complete(download_binaries())
