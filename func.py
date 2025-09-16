# func.py
"""
Utility functions for the Auto Forward Bot
"""

from pyrogram import Client
from pyrogram.errors import FloodWait
import logging
import asyncio
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def copy_content(client, msg, chat_id):
    """
    Copy a message from one chat to another.
    Handles various message types and retries on FloodWait.
    """
    try:
        reply_markup = msg.reply_markup
        has_reply_markup = bool(reply_markup)
        logger.info(f"Copying content from {msg.chat.id} to {chat_id}, has reply_markup: {has_reply_markup}")
        if has_reply_markup:
            logger.info(f"Reply_markup structure: {repr(reply_markup)}")
        if msg.text:
            await client.send_message(chat_id, msg.text, reply_markup=reply_markup)
            logger.info("Text message copied successfully!")
            return True
        elif msg.photo:
            await client.send_photo(chat_id, msg.photo.file_id, caption=msg.caption or '', reply_markup=reply_markup)
            logger.info("Photo copied successfully!")
            return True
        elif msg.video:
            await client.send_video(chat_id, msg.video.file_id, caption=msg.caption or '', reply_markup=reply_markup)
            logger.info("Video copied successfully!")
            return True
        elif msg.sticker:
            await client.send_sticker(chat_id, msg.sticker.file_id, reply_markup=reply_markup)
            logger.info("Sticker copied successfully!")
            return True
        elif msg.document:
            await client.send_document(chat_id, msg.document.file_id, caption=msg.caption or '', reply_markup=reply_markup)
            logger.info("Document copied successfully!")
            return True
        else:
            logger.warning("Unsupported message type, not copied.")
            return False
    except FloodWait as e:
        logger.warning(f"FloodWait: Waiting for {e.x} seconds")
        await asyncio.sleep(e.x)
        return await copy_content(client, msg, chat_id)
    except Exception as e:
        logger.error(f"Error copying content: {str(e)}")
        return False

async def check_admin_status(client, chat_id):
    """
    Check if the bot has admin privileges in the specified chat.
    """
    try:
        chat = await client.get_chat(chat_id)
        logger.info(f"Chat info retrieved for {chat_id}: {chat.title}")
        test_message = await client.send_message(chat_id, "Testing admin privileges...")
        await test_message.delete()
        logger.info(f"Admin test passed for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Admin status check failed for {chat_id}: {str(e)}")
        return False

async def get_channel_name(client, chat_id):
    """
    Retrieve the name of a chat based on its ID.
    """
    try:
        chat = await client.get_chat(chat_id)
        return chat.title
    except Exception as e:
        logger.error(f"Error fetching name for chat {chat_id}: {str(e)}")
        return f"ID: {chat_id} (Inaccessible)"

async def add_channels(client, message, channel_ids, channel_type, channels):
    """
    Add or update channels in the configuration.
    """
    added_count = 0
    added_details = []
    for channel_id_str in channel_ids:
        try:
            channel_id = int(channel_id_str)
            if not channel_id_str.startswith("-100"):
                await message.reply("Invalid format! Channel IDs must start with -100.")
                continue
            is_admin = await check_admin_status(client, channel_id)
            if not is_admin:
                await message.reply(f"Bot lacks full admin privileges in channel {channel_id}. Skipping.")
                continue
            channel_name = await get_channel_name(client, channel_id)
            if channel_type == "sources":
                if channel_id not in channels.get("sources", []):
                    channels["sources"].append(channel_id)
                    added_count += 1
                    added_details.append(f"{channel_name} (ID: {channel_id})")
                else:
                    await message.reply(f"Channel {channel_name} (ID: {channel_id}) is already a source channel.")
            else:  # target
                if channels.get("target") != channel_id:
                    channels["target"] = channel_id
                    added_count += 1
                    added_details.append(f"{channel_name} (ID: {channel_id})")
                else:
                    await message.reply(f"Channel {channel_name} (ID: {channel_id}) is already the target channel.")
                    return
        except ValueError:
            await message.reply(f"Invalid channel ID: {channel_id_str}")
        except Exception as e:
            logger.error(f"Error adding channel {channel_id_str}: {str(e)}")
            await message.reply(f"Error adding channel {channel_id_str}: {str(e)}")
    if added_count > 0:
        details_msg = "\n".join(added_details)
        notification = f"Added/Updated {added_count} {channel_type} channel(s):\n{details_msg}"
        for user_id in users:
            try:
                await client.send_message(user_id, notification)
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {str(e)}")
        await message.reply(notification)
    if message.from_user and message.from_user.id in users_state:
        del users_state[message.from_user.id]

async def list_sources(client, message, channels):
    """
    List all source channels where the bot is an admin.
    """
    if not channels.get("sources", []):
        await message.reply("No source channels set.")
        return
    admin_sources = []
    for source_id in channels["sources"]:
        try:
            is_admin = await check_admin_status(client, source_id)
            if is_admin:
                channel_name = await get_channel_name(client, source_id)
                admin_sources.append(f"{channel_name} (ID: {source_id})")
            else:
                admin_sources.append(f"{source_id} (Bot is not admin)")
        except Exception as e:
            logger.error(f"Error checking source {source_id}: {str(e)}")
            admin_sources.append(f"{source_id} (Error accessing)")
    source_list = "\n".join(admin_sources) if admin_sources else "No accessible sources."
    await message.reply(f"Source Channels where bot is admin:\n{source_list}")

def parse_channel_from_link(link):
    """
    Parse channel ID, username, or invite link from a Telegram link.
    """
    logger.info(f"Parsing link: {link}")
    patterns = [
        r'(?:https?://)?t\.me/c/(\d+)/(\d+)',
        r'(?:https?://)?t\.me/([a-zA-Z0-9_]+)/(\d+)',
        r'(?:https?://)?telegram\.me/([a-zA-Z0-9_]+)/(\d+)',
        r'(?:https?://)?t\.me/\+([a-zA-Z0-9_-]+)/(\d+)',
        r'(?:https?://)?t\.me/joinchat/([a-zA-Z0-9_-]+)/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            channel = match.group(1)
            msg_id = int(match.group(2))
            logger.info(f"Parsed link: channel={channel}, msg_id={msg_id}")
            return channel, msg_id
    logger.warning(f"Failed to parse link: {link}")
    return None, None

async def resolve_channel(client, channel_identifier):
    """
    Resolve channel identifier (username, invite link, or ID) to chat ID.
    """
    logger.info(f"Resolving channel: {channel_identifier}")
    try:
        if channel_identifier.startswith("-100"):
            logger.info(f"Direct chat ID provided: {channel_identifier}")
            return int(channel_identifier)
        elif re.match(r'^\d+$', channel_identifier):
            chat_id = -int(f"100{channel_identifier}")
            logger.info(f"Converted t.me/c numeric ID to chat ID: {chat_id}")
            try:
                chat = await client.get_chat(chat_id)
                logger.info(f"Successfully accessed chat: {chat.title} (ID: {chat_id})")
                return chat_id
            except (ChatInvalid, PeerIdInvalid):
                logger.error(f"Bot cannot access chat ID {chat_id}. Ensure bot is a member.")
                return None
        elif channel_identifier.startswith("+") or "/joinchat/" in channel_identifier:
            logger.info(f"Attempting to join chat via invite link: {channel_identifier}")
            chat = await client.join_chat(channel_identifier)
            logger.info(f"Joined chat: {chat.title} (ID: {chat.id})")
            return chat.id
        else:
            logger.info(f"Attempting to resolve username: {channel_identifier}")
            chat = await client.get_chat(channel_identifier)
            logger.info(f"Resolved username to chat: {chat.title} (ID: {chat.id})")
            return chat.id
    except UsernameInvalid:
        logger.error(f"Invalid username or invite link: {channel_identifier}")
        return None
    except (ChatInvalid, PeerIdInvalid):
        logger.error(f"Cannot access channel: {channel_identifier}. Bot may not be a member or lack permissions.")
        return None
    except Exception as e:
        logger.error(f"Error resolving channel {channel_identifier}: {str(e)}")
        return None
