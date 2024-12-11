import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from BrandrdXMusic.utils.database import get_assistant
from BrandrdXMusic import app
from BrandrdXMusic.utils.branded_ban import admin_filter

SPAM_CHATS = []

@app.on_message(
    filters.command(
        ["atag", "aall", "amention", "amentionall"], prefixes=["/", "@", ".", "#"]
    )
    & admin_filter
)
async def atag_all_users(_, message):
    # Fetch the userbot (assistant) instance
    userbot = await get_assistant(message.chat.id)
    
    # Prevent multiple tagging processes in the same chat
    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ. ᴛᴏ sᴛᴏᴘ, ᴜsᴇ `/acancel`."
        )
    
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        # Notify user to provide text for tagging
        await message.reply_text(
            "**Provide text to tag all users, like:** `/aall Hi Friends`"
        )
        return

    # Add chat ID to SPAM_CHATS to mark the process as ongoing
    SPAM_CHATS.append(message.chat.id)
    usernum = 0
    usertxt = ""

    # Handle replied text for tagging
    if replied:
        async for member in app.get_chat_members(message.chat.id):
            # Stop process if `/acancel` is called
            if message.chat.id not in SPAM_CHATS:
                break
            
            usernum += 1
            usertxt += f"[{member.user.first_name}](tg://openmessage?user_id={member.user.id}) "

            if usernum == 14:  # Send message in batches of 14 users
                await userbot.send_message(
                    message.chat.id,
                    f"{replied.text}\n\n{usertxt}",
                    disable_web_page_preview=True,
                )
                await asyncio.sleep(2)  # Pause to avoid hitting FloodWait
                usernum = 0
                usertxt = ""

    # Handle custom text for tagging
    else:
        text = message.text.split(None, 1)[1]

        async for member in app.get_chat_members(message.chat.id):
            if message.chat.id not in SPAM_CHATS:
                break
            
            usernum += 1
            usertxt += f'<a href="tg://openmessage?user_id={member.user.id}">{member.user.first_name}</a> '

            if usernum == 14:  # Send message in batches of 14 users
                await userbot.send_message(
                    message.chat.id, f"{text}\n{usertxt}", disable_web_page_preview=True
                )
                await asyncio.sleep(2)  # Pause to avoid hitting FloodWait
                usernum = 0
                usertxt = ""

    # Cleanup: remove chat ID from SPAM_CHATS once tagging is complete
    try:
        SPAM_CHATS.remove(message.chat.id)
    except Exception:
        pass


@app.on_message(filters.command("acancel", prefixes=["/", "@", ".", "#"]))
async def cancelcmd(_, message):
    chat_id = message.chat.id

    if chat_id in SPAM_CHATS:
        try:
            # Remove chat ID from SPAM_CHATS to stop tagging
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass
        
        await message.reply_text("**ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss sᴜᴄᴄᴇssғᴜʟʟʏ sᴛᴏᴘᴘᴇᴅ!**")
    else:
        # Notify user if no tagging process is ongoing
        await message.reply_text("**ɴᴏ ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss ɪs ᴏɴɢᴏɪɴɢ!**")
