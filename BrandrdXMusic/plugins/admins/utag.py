import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPermissions
from BrandrdXMusic import app
from BrandrdXMusic.utils.branded_ban import admin_filter

SPAM_TASKS = {}

# Start unlimited tagging
@app.on_message(
    filters.command(["utag", "uall"], prefixes=["/", "@", ".", "#"]) & admin_filter
)
async def tag_all_users(_, message):
    global SPAM_TASKS
    chat_id = message.chat.id

    # Check if no text is provided after the command
    if len(message.text.split()) == 1:
        await message.reply_text(
            "** ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ, ʟɪᴋᴇ »** `@utag Hi Friends`"
        )
        return

    # Get the text to be sent with tags
    text = message.text.split(None, 1)[1]
    if text:
        await message.reply_text(
            "**ᴜᴛᴀɢ [ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢ] sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n**๏ ᴛᴀɢɢɪɴɢ ᴡɪᴛʜ sʟᴇᴇᴘ ᴏғ 7 sᴇᴄ.**\n\n**➥ ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » /stoputag**"
        )

    # Cancel any ongoing task for the chat
    if chat_id in SPAM_TASKS:
        SPAM_TASKS[chat_id].cancel()

    # Create a new task for tagging
    SPAM_TASKS[chat_id] = asyncio.create_task(tag_users(chat_id, text, message))


async def tag_users(chat_id, text, message):
    try:
        usernum = 0
        usertxt = ""

        # Iterate through all chat members
        async for m in app.get_chat_members(chat_id):
            if m.user.is_bot:
                continue
            usernum += 1
            usertxt += f"\n⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"

            # Send tag message in batches of 5 users
            if usernum == 5:
                await app.send_message(
                    chat_id,
                    f"{text}\n{usertxt}\n\n|| ➥ ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » /stoputag ||",
                )
                usernum = 0
                usertxt = ""
                await asyncio.sleep(7)  # Delay to avoid spam
    except asyncio.CancelledError:
        await message.reply_text("**ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢɢɪɴɢ ᴄᴀɴᴄᴇʟʟᴇᴅ ɪɴsᴛᴀɴᴛʟʏ!**")
    except Exception as e:
        print(e)


# Stop unlimited tagging
@app.on_message(
    filters.command(
        ["stoputag", "stopuall", "offutag", "offuall", "utagoff", "ualloff"],
        prefixes=["/", ".", "@", "#"],
    )
    & admin_filter
)
async def stop_tagging(_, message):
    global SPAM_TASKS
    chat_id = message.chat.id

    # Cancel the task if it's running
    if chat_id in SPAM_TASKS and not SPAM_TASKS[chat_id].done():
        SPAM_TASKS[chat_id].cancel()
        del SPAM_TASKS[chat_id]
        await message.reply_text("**ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ ɪɴsᴛᴀɴᴛʟʏ!**")
    else:
        await message.reply_text("**ᴜᴛᴀɢ ᴘʀᴏᴄᴇss ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ**")
