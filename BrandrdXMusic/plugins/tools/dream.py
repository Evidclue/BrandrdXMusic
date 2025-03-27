import os
import google.generativeai as genai
import asyncio
import time
from pyrogram import filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from BrandrdXMusic import app

# ✅ Secure API Key Retrieval
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Gemini API Key is missing! Set it in environment variables.")

# ✅ Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# ✅ AI Model Selection
MODEL_NAME = "models/gemini-2.0-flash"

# ✅ Storage for Auto AI Mode & Context
AUTO_AI_MODE = {}
USER_CONTEXT = {}
LAST_REPLY_TIME = {}
MESSAGE_QUEUE = asyncio.Queue()  # ✅ Async Queue to Process AI Replies

# ✅ Telegram-Compatible Bold Text
def bold_text(text):
    return f"**{text}**"

# ✅ Help Button
HELP_BUTTON = [[InlineKeyboardButton("💡 " + bold_text("Need Help?"), callback_data="help_ai")]]

# ✅ Enable AI Auto-Reply
@app.on_message(filters.command("d on") & filters.group)
async def enable_auto_ai(bot, message):
    AUTO_AI_MODE[message.chat.id] = True
    await message.reply_text(f"🌌 {bold_text('Dream Mode Enabled!')}\nAI will respond to song/video commands.\nUse `/d off` to disable.")

# ✅ Disable AI Auto-Reply
@app.on_message(filters.command(["d off", "d cancel"]) & filters.group)
async def disable_auto_ai(bot, message):
    AUTO_AI_MODE[message.chat.id] = False
    await message.reply_text(f"❌ {bold_text('Dream Mode Disabled!')}\nUse `/d on` to enable again.")

# ✅ Auto AI Response in Group (Flood-Proof)
@app.on_message(filters.group & filters.text)
async def auto_ai_respond(bot, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if AUTO_AI_MODE.get(chat_id, False):
        current_time = time.time()

        # ✅ Prevent Spam (5-Second Cooldown per User)
        if user_id in LAST_REPLY_TIME and current_time - LAST_REPLY_TIME[user_id] < 5:
            return
        LAST_REPLY_TIME[user_id] = current_time

        # ✅ Check if message starts with /play or /vplay
        if message.text.startswith("/play") or message.text.startswith("/vplay"):
            # ✅ Add Message to Processing Queue
            await MESSAGE_QUEUE.put((message, chat_id, user_id))

# ✅ AI Response Worker (Prevents FloodWait & Crashes)
async def message_worker():
    while True:
        message, chat_id, user_id = await MESSAGE_QUEUE.get()

        try:
            processing_msg = await message.reply_text("🤖 " + bold_text("Ada Thinking..."))

            # ✅ Get AI Response for Song/Video
            response_text = await get_song_related_response(user_id, message.text)

            # ✅ Handle FloodWait
            try:
                await processing_msg.edit(response_text)
            except FloodWait as e:
                await asyncio.sleep(e.value)  # ✅ Wait and retry
                await message.reply_text(response_text)
            except RPCError:
                await message.reply_text(response_text)

            await asyncio.sleep(3)  # ✅ Short delay to prevent API spam
        except Exception as e:
            print(f"⚠ AI Worker Error: {str(e)}")

# ✅ Start AI Worker in Background
asyncio.create_task(message_worker())

# ✅ Fetch Song/Video Related AI Response
async def get_song_related_response(user_id, user_input):
    if user_id not in USER_CONTEXT:
        USER_CONTEXT[user_id] = []

    # ✅ Extract song/video title from /play or /vplay command
    command_parts = user_input.split(" ", 1)  # Split into command and rest
    if len(command_parts) < 2:
        return f"⚠ {bold_text('Please provide a song or video title!')} Example: `/play Tum Hi Ho`"

    song_title = command_parts[1].strip()  # Get the song/video title
    USER_CONTEXT[user_id].append(f"User: Requested {song_title}")

    # ✅ Keep Last 3 Messages for Context
    conversation_history = "\n".join(USER_CONTEXT[user_id][-3:])

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # ✅ Prompt AI to generate a related response
        prompt = f"Generate a short response related to the song or video titled '{song_title}'. For example, mention a similar song, artist, or a fun fact."
        response = model.generate_content(prompt)

        ai_reply = response.text.strip()

        # ✅ Limit Response Size to 5-15 words
        words = ai_reply.split()
        if len(words) > 15:
            ai_reply = " ".join(words[:15])
        elif len(words) < 5:
            ai_reply = " ".join(words + [""] * (5 - len(words)))

        USER_CONTEXT[user_id].append(f"AI: {ai_reply}")  # ✅ Store AI Response
        return ai_reply
    except Exception as e:
        return f"⚠ {bold_text('AI Error:')} {str(e)}"

# ✅ AI Help Callback Handler
@app.on_callback_query(filters.regex("help_ai"))
async def ai_callback(client, query):
    await query.message.edit_text(f"💡 {bold_text('Ada Chat Guide:')}\n\n💬 {bold_text('Type:')} `/play <song>` or `/vplay <video>`\n📌 {bold_text('Example:')} `/play Tum Hi Ho`",
                                  reply_markup=InlineKeyboardMarkup(HELP_BUTTON))
