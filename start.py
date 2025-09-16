# start.py
"""
Welcome and initial interaction handlers for the Auto Forward Bot
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import initialize_channels, load_users, save_channels
from func import copy_content, check_admin_status, get_channel_name, add_channels, list_sources
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Variables
channels = initialize_channels()
users = load_users()
users_state = {}

# Handler Functions
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
        users_collection.insert_one({"user_id": user_id})
    source_list = ", ".join([await get_channel_name(client, s) for s in channels.get("sources", [])]) if channels.get("sources", []) else "Not set"
    target = await get_channel_name(client, channels["target"]) if channels.get("target") else "Not set"
    selected_source = await get_channel_name(client, channels["selected_source"]) if channels.get("selected_source") else "Not set"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("Creator", callback_data="creator")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ])
    await message.reply(
        f"Hi There... {message.from_user.mention} ❄️\n\n"
        f"Created by {OWNER_NAME}.\n"
        f"This bot copies new messages from all source channels to the target channel when added as an admin.\n\n"
        f"Sources: {source_list}\n"
        f"Selected Source (for manual copying): {selected_source}\n"
        f"Target: {target}",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^help$"))
async def callback_help(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Select Source", callback_data="select_source")
        ],
        [
            InlineKeyboardButton("Set Sources", callback_data="set_sources"),
            InlineKeyboardButton("Set Target", callback_data="set_target")
        ],
        [
            InlineKeyboardButton("Back to Home", callback_data="back_home")
        ]
    ])
    await callback_query.message.edit_text(
        "Bot Commands and Usage:\n"
        "- /setsource <channel_id>: Adds a source channel for real-time copying.\n"
        "- /removesource <channel_id>: Removes a source channel.\n"
        "- /settarget <channel_id>: Sets the target channel.\n"
        "- /listsources: Lists all source channels where bot is admin.\n"
        "- /selectsource: Select a source channel for manual copying of old messages.\n"
        "- /copy <message_id_or_link> [source_id]: Copies a message from selected or specified source.\n"
        "- /ncopy <start_id> <batch_size> [source_id]: Copies a range of messages from selected or specified source.",
        reply_markup=keyboard
    )
    await callback_query.answer()

@app.on_callback_query(filters.regex(r"^creator$"))
async def callback_creator(client, callback_query):
    await callback_query.message.edit_text(
        f"Bot created by {OWNER_NAME} ❄️\n\n"
        "Thanks for using this bot!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back to Home", callback_data="back_home")]
        ])
    )
    await callback_query.answer()

@app.on_callback_query(filters.regex(r"^close$"))
async def close_message(client, callback_query):
    await callback_query.message.delete()
    await callback_query.answer()

@app.on_callback_query(filters.regex(r"^back_home$"))
async def back_home(client, callback_query):
    source_list = ", ".join([await get_channel_name(client, s) for s in channels.get("sources", [])]) if channels.get("sources", []) else "Not set"
    target = await get_channel_name(client, channels["target"]) if channels.get("target") else "Not set"
    selected_source = await get_channel_name(client, channels["selected_source"]) if channels.get("selected_source") else "Not set"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("Creator", callback_data="creator")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ])
    await callback_query.message.edit_text(
        f"Hi There... {callback_query.from_user.mention} ❄️\n\n"
        f"Created by {OWNER_NAME}.\n"
        f"This bot copies new messages from all source channels to the target channel when added as an admin.\n\n"
        f"Sources: {source_list}\n"
        f"Selected Source (for manual copying): {selected_source}\n"
        f"Target: {target}",
        reply_markup=keyboard
    )
    await callback_query.answer()

# Run the Client
if __name__ == "__main__":
    app.run()
