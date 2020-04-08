from telethon import TelegramClient
import os
import time


client = TelegramClient('binaries-monsta-omnomnom', os.environ['API_ID'], os.environ['API_HASH'])


#writing pid to file so we can echo to stdin(/proc/pid/fd/0) to pass on the confirmation code for telegram login
pid = os.getpid()
with open('dragndrop.pid', 'w') as f:
   f.write(str(pid))


async def download_binaries():
    last_msg = await client.get_messages('komodo_sync_bot', 2)
    last_msg = last_msg[1]
    if last_msg.document:
        await last_msg.download_media('/root/new-binaries.zip')


with client:
    client.loop.run_until_complete(download_binaries())
