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
DREAM_MODE = {}
USER_CONTEXT = {}
LAST_REPLY_TIME = {}
MESSAGE_QUEUE = asyncio.Queue()  # ✅ Async Queue to Process AI Replies

# ✅ Telegram-Compatible Bold Text
def bold_text(text):
    return f"**{text}**"

# ✅ Help Button
HELP_BUTTON = [[InlineKeyboardButton("💡 " + bold_text("Need Help?"), callback_data="help_ai")]]

# ✅ Enable AI Auto-Reply
@app.on_message(filters.command("ai on") & filters.group)
async def enable_auto_ai(bot, message):
    AUTO_AI_MODE[message.chat.id] = True
    await message.reply_text(f"🤖 {bold_text('AI Auto-Reply Enabled!')}\nJust type, and AI will respond.\nUse `/ai off` to disable.")

# ✅ Disable AI Auto-Reply
@app.on_message(filters.command(["ai off", "ai cancel"]) & filters.group)
async def disable_auto_ai(bot, message):
    AUTO_AI_MODE[message.chat.id] = False
    await message.reply_text(f"❌ {bold_text('AI Auto-Reply Disabled!')}\nUse `/ai on` to enable again.")

# ✅ Enable Dream Mode
@app.on_message(filters.command("d on") & filters.group)
async def enable_dream_mode(bot, message):
    DREAM_MODE[message.chat.id] = True
    await message.reply_text(f"🎵 {bold_text('Dream Mode Enabled!')}\nAuto-play related songs.\nUse `/d off` to disable.")

# ✅ Disable Dream Mode
@app.on_message(filters.command("d off") & filters.group)
async def disable_dream_mode(bot, message):
    DREAM_MODE[message.chat.id] = False
    await message.reply_text(f"❌ {bold_text('Dream Mode Disabled!')}\nUse `/d on` to enable again.")

# ✅ AI Chat Command
@app.on_message(filters.command("ai"))
async def ai_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(f"💡 {bold_text('Usage:')} `/ai <message>`\n📌 {bold_text('Example:')} `/ai What is Quantum Physics?`",
                                 reply_markup=InlineKeyboardMarkup(HELP_BUTTON))
        return

    user_id = message.from_user.id
    user_input = message.reply_to_message.text if message.reply_to_message else " ".join(message.command[1:])

    # ✅ Display "Thinking..." Message
    processing_msg = await message.reply_text("🤖 " + bold_text("Ada Thinking..."))

    # ✅ Fetch AI Response
    response_text = await get_ai_response(user_id, user_input)

    final_response = f"💬 {bold_text('AI Response:')}\n\n{response_text}\n\n🔹 {bold_text('Powered by AI')}"

    # ✅ Prevent FloodWait
    try:
        await processing_msg.edit(final_response)
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait for FloodWait duration
        await message.reply_text(final_response)
    except RPCError:
        await message.reply_text(final_response)

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

        # ✅ Add Message to Processing Queue
        await MESSAGE_QUEUE.put((message, chat_id, user_id))

    # ✅ Handle Dream Mode
    if DREAM_MODE.get(chat_id, False) and (message.text.startswith("/play ") or message.text.startswith("/vplay ")):
        song_query = message.text.split(maxsplit=1)[1]
        related_song = await get_related_song(song_query)
        if related_song:
            await message.reply_text(f"🎵 {bold_text('Related Song:')} {related_song}")

# ✅ AI Response Worker (Prevents FloodWait & Crashes)
async def message_worker():
    while True:
        message, chat_id, user_id = await MESSAGE_QUEUE.get()

        try:
            processing_msg = await message.reply_text("🤖 " + bold_text("Ada Thinking..."))

            # ✅ Get AI Response
            response_text = await get_ai_response(user_id, message.text)
            final_response = f"💬 {bold_text('AI Response:')}\n\n{response_text}\n\n🔹 {bold_text('Powered by AI')}"

            # ✅ Handle FloodWait
            try:
                await processing_msg.edit(final_response)
            except FloodWait as e:
                await asyncio.sleep(e.value)  # ✅ Wait and retry
                await message.reply_text(final_response)
            except RPCError:
                await message.reply_text(final_response)

            await asyncio.sleep(3)  # ✅ Short delay to prevent API spam
        except Exception as e:
            print(f"⚠ AI Worker Error: {str(e)}")

# ✅ Start AI Worker in Background
asyncio.create_task(message_worker())

# ✅ Fetch AI Response with Memory Optimization
async def get_ai_response(user_id, user_input):
    if user_id not in USER_CONTEXT:
        USER_CONTEXT[user_id] = []

    USER_CONTEXT[user_id].append(f"User: {user_input}")

    # ✅ Keep Last 3 Messages for Context
    conversation_history = "\n".join(USER_CONTEXT[user_id][-3:])

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(conversation_history)

        ai_reply = response.text.strip()

        # ✅ Limit Response Size
        if len(ai_reply) > 4096:
            ai_reply = ai_reply[:4000] + "... (Truncated)"

        USER_CONTEXT[user_id].append(f"AI: {ai_reply}")  # ✅ Store AI Response
        return ai_reply
    except Exception as e:
        return f"⚠ {bold_text('AI Error:')} {str(e)}"

# ✅ Fetch Related Song Using Gemini AI
async def get_related_song(song_query):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(f"Find a related song to '{song_query}'")

        related_song = response.text.strip().split("\n")[0]  # Take the first suggestion
        return related_song
    except Exception as e:
        return f"⚠ {bold_text('AI Error:')} {str(e)}"

# ✅ AI Help Callback Handler
@app.on_callback_query(filters.regex("help_ai"))
async def ai_callback(client, query):
    await query.message.edit_text(f"💡 {bold_text('Ada Chat Guide:')}\n\n💬 {bold_text('Type:')} `/ai <message>`\n📌 {bold_text('Example:')} `/ai What is Gravity?`",
                                  reply_markup=InlineKeyboardMarkup(HELP_BUTTON))
