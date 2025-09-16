from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, MAX_BATCH_SIZE, ADMINS, OWNER_NAME
from database import initialize_channels, load_users, save_channels
from func import copy_content, check_admin_status, get_channel_name, add_channels, list_sources, parse_channel_from_link, resolve_channel
import logging
from start import start, callback_help, callback_creator, close_message, back_home, set_sources_callback, set_target_callback, select_source_callback, source_selected_callback, handle_user_input, realtime_copy_specific, setsource_command, removesource_command, listsources_command, settarget_command, selectsource_command, copy_command, ncopy, broadcast_command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Global Variables
channels = initialize_channels()
users = load_users()
users_state = {}

# Initialize Telegram Client
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Register Handlers
app.on_message(filters.command("start"))(start)
app.on_callback_query(filters.regex(r"^help$"))(callback_help)
app.on_callback_query(filters.regex(r"^creator$"))(callback_creator)
app.on_callback_query(filters.regex(r"^close$"))(close_message)
app.on_callback_query(filters.regex(r"^back_home$"))(back_home)
app.on_callback_query(filters.regex(r"^set_sources$"))(set_sources_callback)
app.on_callback_query(filters.regex(r"^set_target$"))(set_target_callback)
app.on_callback_query(filters.regex(r"^select_source$"))(select_source_callback)
app.on_callback_query(filters.regex(r"^source_(-100\d+)$"))(source_selected_callback)
app.on_message(filters.private & ~filters.command(["start", "setsource", "removesource", "settarget", "listsources", "selectsource", "copy", "ncopy", "broadcast"]))(
    handle_user_input)
app.on_message(filters.chat(channels.get("sources", [])))(realtime_copy_specific)
app.on_message(filters.command("setsource"))(setsource_command)
app.on_message(filters.command("removesource"))(removesource_command)
app.on_message(filters.command("listsources"))(listsources_command)
app.on_message(filters.command("settarget"))(settarget_command)
app.on_message(filters.command("selectsource"))(selectsource_command)
app.on_message(filters.command("copy"))(copy_command)
app.on_message(filters.command("ncopy"))(ncopy)
app.on_message(filters.command("broadcast") & filters.user(ADMINS))(broadcast_command)

# Run the Bot
if __name__ == "__main__":
    logger.info("Starting Auto Forward Bot...")
    app.run()
  
