import time
import pytz
import asyncio
import uvloop
import importlib
from pytz import utc
from pyrogram import Client
from Music.config import AUTO_LEAVE
from Music.config import API_ID, API_HASH, BOT_TOKEN, MONGO_DB_URI, SUDO_USERS, LOG_GROUP_ID
from Music import BOT_NAME, ASSNAME, app, client
from Music.MusicUtilities.database.functions import clean_restart_stage
from Music.MusicUtilities.database.queue import get_active_chats, remove_active_chat
from Music.MusicUtilities.tgcallsrun import run
from pytgcalls import idle
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from Music.MusicUtilities.helpers.autoleave import leave_from_inactive_call
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

scheduler = AsyncIOScheduler()

# Retry logic for database operations
async def retry_db_operation(operation, retries=5, delay=1):
    for attempt in range(retries):
        try:
            return await operation()
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e).lower():
                logging.warning(f"Database locked, retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise
    raise Exception('Max retries exceeded for database operation')

async def clean_restart_stage_retry():
    return await retry_db_operation(clean_restart_stage)

async def get_active_chats_retry():
    return await retry_db_operation(get_active_chats)

async def remove_active_chat_retry(chat_id):
    return await retry_db_operation(lambda: remove_active_chat(chat_id))

async def load_start():
    restart_data = await clean_restart_stage_retry()
    if restart_data:
        print("[INFO]: SENDING RESTART STATUS TO SERVER")
        try:
            await app.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "**Restarted the Bot Successfully.**",
            )
        except Exception as e:
            logging.error(f"Failed to send restart status: {e}")
    
    served_chats = []
    try:
        chats = await get_active_chats_retry()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        logging.error(f"Error while retrieving active chats: {e}")
    
    for served_chat in served_chats:
        try:
            await remove_active_chat_retry(served_chat)
        except Exception as e:
            logging.error(f"Error while removing active chat {served_chat}: {e}")
    
    await app.send_message(LOG_GROUP_ID, "Bot Started")
    print("[INFO]: STARTED BOT AND SENDING THE INFO TO SERVER")
    
    if AUTO_LEAVE:
        print("[ INFO ] STARTING SCHEDULER")
        scheduler.configure(timezone=pytz.utc)
        scheduler.add_job(
            leave_from_inactive_call, "interval", seconds=AUTO_LEAVE
        )
        scheduler.start()

async def main():
    async with Client(
        ':Music:',
        API_ID,
        API_HASH,
        bot_token=BOT_TOKEN,
        plugins={'root': 'Music.Plugins'}
    ) as client:
        await load_start()
        run()
        await idle()

# Run the main function
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()
    print("[LOG] CLOSING BOT")
