import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPermissions
from BrandrdXMusic import app
from BrandrdXMusic.utils.branded_ban import admin_filter

SPAM_CHATS = {}


@app.on_message(
    filters.command(["utag", "uall"], prefixes=["/", "@", ".", "#"]) & admin_filter
)
async def tag_all_users(_, message):
    global SPAM_CHATS
    chat_id = message.chat.id
    if len(message.text.split()) == 1:
        await message.reply_text(
            "** ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ, ʟɪᴋᴇ »** `@utag Hi Friends`"
        )
        return

    text = message.text.split(None, 1)[1]
    await message.reply_text(
        "**ᴜᴛᴀɢ [ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢ] sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
        "**๏ ᴛᴀɢɢɪɴɢ ᴡɪᴛʜ sʟᴇᴇᴘ ᴏғ 7 sᴇᴄ.**\n\n"
        "**➥ ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » /stoputag**"
    )

    SPAM_CHATS[chat_id] = True
    try:
        while SPAM_CHATS.get(chat_id, False):
            usernum = 0
            usertxt = ""
            async for m in app.get_chat_members(chat_id):
                if not SPAM_CHATS.get(chat_id, False):
                    break  # Stop tagging immediately
                if m.user.is_bot:
                    continue
                usernum += 1
                usertxt += f"\n⊚ [{m.user.first_name}](tg://user?id={m.user.id})"
                if usernum == 5:
                    await app.send_message(
                        chat_id,
                        f"{text}\n{usertxt}\n\n|| ➥ ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » /stoputag ||",
                    )
                    usernum = 0
                    usertxt = ""
                    await asyncio.sleep(7)  # Pause between batches
    except Exception as e:
        print(f"Error in tagging: {e}")
    finally:
        SPAM_CHATS.pop(chat_id, None)  # Clean up the dictionary entry

@app.on_message(
    filters.command(
        ["stoputag", "stopuall", "offutag", "offuall", "utagoff", "ualloff"],
        prefixes=["/", ".", "@", "#"],
    )
    & admin_filter
)
async def stop_tagging(_, message):
    global SPAM_CHATS
    chat_id = message.chat.id
    if SPAM_CHATS.get(chat_id, False):
        SPAM_CHATS[chat_id] = False  # Signal to stop tagging
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘɪɴɢ!**")
    else:
        await message.reply_text("**ᴜᴛᴀɢ ᴘʀᴏᴄᴇss ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ.**")
