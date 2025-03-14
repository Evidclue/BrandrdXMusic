import os
import google.generativeai as genai
import asyncio
import time
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from BrandrdXMusic import app

# ✅ Securely Fetch Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Gemini API Key is missing! Set it in environment variables.")

# ✅ Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# ✅ AI Model Selection
MODEL_NAME = "models/gemini-2.0-flash"

# ✅ Storage for AI Auto-Reply Mode & User Context
AUTO_AI_MODE = {}
USER_CONTEXT = {}
LAST_REPLY_TIME = {}
MESSAGE_QUEUE = asyncio.Queue()  # ✅ Async Message Queue for FloodWait Handling

# ✅ Bold Function (Telegram-compatible)
def bold_text(text):
    return f"**{text}**"  # ✅ Telegram uses `**text**` for bold formatting

# ✅ Inline Button for AI Help
HELP_BUTTON = [[InlineKeyboardButton("💡 " + bold_text("Need Help?"), callback_data="help_ai")]]

# ✅ Enable AI Auto-Reply in Group
@app.on_message(filters.command("ai on") & filters.group)
async def enable_auto_ai(bot, message):
    AUTO_AI_MODE[message.chat.id] = True
    await message.reply_text(f"🤖 {bold_text('AI Auto-Reply Enabled!')}\n\nJust type, and AI will respond.\nUse `/ai off` to disable.")

# ✅ Disable AI Auto-Reply in Group
@app.on_message(filters.command(["ai off", "ai cancel"]) & filters.group)
async def disable_auto_ai(bot, message):
    AUTO_AI_MODE[message.chat.id] = False
    await message.reply_text(f"❌ {bold_text('AI Auto-Reply Disabled!')}\n\nUse `/ai on` to enable again.")

# ✅ AI Chat Handler
@app.on_message(filters.command("ai"))
async def ai_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(f"💡 {bold_text('Usage:')} `/ai <your message>`\n📌 {bold_text('Example:')} `/ai What is Quantum Physics?`",
                                 reply_markup=InlineKeyboardMarkup(HELP_BUTTON))
        return

    user_id = message.from_user.id
    user_input = message.reply_to_message.text if message.reply_to_message else " ".join(message.command[1:])

    processing_msg = await message.reply_text("🤖 " + bold_text("Thinking..."))

    # ✅ Get AI Response
    response_text = await get_ai_response(user_id, user_input)

    final_response = f"💬 {bold_text('AI Response:')}\n\n{response_text}\n\n🔹 {bold_text('Powered by AI')}"

    try:
        await processing_msg.edit(final_response)
    except FloodWait as e:
        print(f"⚠ FloodWait triggered! Waiting for {e.value} seconds...")
        await asyncio.sleep(e.value)
        await message.reply_text(final_response)

# ✅ Auto AI Response in Group (With 5-Second Cooldown & Queue Processing)
@app.on_message(filters.group & filters.text)
async def auto_ai_respond(bot, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if AUTO_AI_MODE.get(chat_id, False):
        current_time = time.time()

        # ✅ Prevent spam (5 sec cooldown per user)
        if user_id in LAST_REPLY_TIME and current_time - LAST_REPLY_TIME[user_id] < 5:
            return
        LAST_REPLY_TIME[user_id] = current_time

        processing_msg = await message.reply_text("🤖 " + bold_text("Thinking..."))

        # ✅ Add to async message queue
        await MESSAGE_QUEUE.put((processing_msg.chat.id, processing_msg.id, message.text))

# ✅ AI Response Worker (Prevents FloodWait & Ensures Smooth Responses)
async def message_worker():
    while True:
        chat_id, message_id, user_input = await MESSAGE_QUEUE.get()

        try:
            response_text = await get_ai_response(chat_id, user_input)
            final_response = f"💬 {bold_text('AI Response:')}\n\n{response_text}\n\n🔹 {bold_text('Powered by AI')}"

            await app.edit_message_text(chat_id, message_id, final_response)

            await asyncio.sleep(5)  # ✅ 5 sec delay to prevent FloodWait
        except FloodWait as e:
            print(f"⚠ FloodWait triggered! Waiting for {e.value} seconds...")
            await asyncio.sleep(e.value)
            await app.send_message(chat_id, final_response)

# ✅ Start AI Worker in Background
asyncio.create_task(message_worker())

# ✅ Fetch AI Response with User Memory (Optimized for Stability)
async def get_ai_response(user_id, user_input):
    if user_id not in USER_CONTEXT:
        USER_CONTEXT[user_id] = []

    USER_CONTEXT[user_id].append(f"User: {user_input}")

    # ✅ Keep only last 3 messages in memory
    conversation_history = "\n".join(USER_CONTEXT[user_id][-3:])

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(conversation_history)

        ai_reply = response.text.strip()

        # ✅ Limit response size (Split if > 4096 characters)
        if len(ai_reply) > 4096:
            ai_reply = ai_reply[:4000] + "... (Truncated)"

        USER_CONTEXT[user_id].append(f"AI: {ai_reply}")  # ✅ Store AI response in memory
        return ai_reply
    except Exception as e:
        return f"⚠ {bold_text('AI Error:')} {str(e)}"

# ✅ AI Help Callback Handler
@app.on_callback_query(filters.regex("help_ai"))
async def ai_callback(client, query):
    await query.message.edit_text(f"💡 {bold_text('Ada Chat Guide:')}\n\n💬 {bold_text('Type:')} `/ai <message>`\n📌 {bold_text('Example:')} `/ai What is Gravity?`",
                                  reply_markup=InlineKeyboardMarkup(HELP_BUTTON))
