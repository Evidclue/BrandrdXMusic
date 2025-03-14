import os
import shutil
from re import findall
from bing_image_downloader import downloader
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message
from BrandrdXMusic import app

# Owner ID (Full control for approving/demoting users)
OWNER_ID = 7732630047

# Set to keep track of approved users
approved_users = set()

@app.on_message(filters.command(["imgs", "image"], prefixes=["/", "!"]))
async def google_img_search(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the user is OWNER or approved
    if user_id != OWNER_ID and user_id not in approved_users:
        return await message.reply("❌ You are not authorized to use this command!")

    try:
        query = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply("ℹ️ Please provide a query to search for images!")

    lim = findall(r"lim=\d+", query)
    try:
        lim = int(lim[0].replace("lim=", ""))
        query = query.replace(f"lim={lim}", "")
    except IndexError:
        lim = 5  # Default limit to 5 images

    download_dir = "downloads"

    try:
        downloader.download(query, limit=lim, output_dir=download_dir, adult_filter_off=True, force_replace=False, timeout=60)
        images_dir = os.path.join(download_dir, query)
        if not os.listdir(images_dir):
            raise Exception("No images were downloaded.")
        lst = [os.path.join(images_dir, img) for img in os.listdir(images_dir)][:lim]  # Ensure we only take the number of images specified by lim
    except Exception as e:
        return await message.reply(f"❌ Error downloading images: {e}")

    msg = await message.reply("🔍 𝔸𝕕𝕒 𝕊𝕖𝕒𝕣𝕔𝕙𝕚𝕟𝕘 𝕒𝕟𝕕 𝕕𝕠𝕨𝕟𝕝𝕠𝕒𝕕𝕚𝕟𝕘 𝕚𝕞𝕒𝕘𝕖𝕤...")

    count = 0
    for img in lst:
        count += 1
        await msg.edit(f"=> 🔍 𝔸𝕕𝕒 𝕠𝕨𝕠 𝕤𝕔𝕣𝕒𝕡𝕡𝕖𝕕 𝕚𝕞𝕒𝕘𝕖𝕤 {count}")

    try:
        await app.send_media_group(
            chat_id=chat_id,
            media=[InputMediaPhoto(media=img) for img in lst],
            reply_to_message_id=message.id
        )
        shutil.rmtree(images_dir)
        await msg.delete()
    except Exception as e:
        await msg.delete()
        return await message.reply(f"❌ Error sending images: {e}")

@app.on_message(filters.command(["image approve"], prefixes=["/", "!"]) & filters.user(OWNER_ID))
async def approve_user(client: Client, message: Message):
    # Approve a user to use /imgs or /image commands
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("ℹ️ Please reply to the user you want to approve!")

    user_id = message.reply_to_message.from_user.id
    approved_users.add(user_id)
    await message.reply(f"✅ User {user_id} is now approved to use /imgs and /image commands!")

@app.on_message(filters.command(["image demote"], prefixes=["/", "!"]) & filters.user(OWNER_ID))
async def demote_user(client: Client, message: Message):
    # Demote a user, removing their ability to use /imgs or /image commands
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("ℹ️ Please reply to the user you want to demote!")

    user_id = message.reply_to_message.from_user.id
    if user_id in approved_users:
        approved_users.remove(user_id)
        await message.reply(f"✅ User {user_id} is no longer approved to use /imgs and /image commands!")
    else:
        await message.reply(f"ℹ️ User {user_id} was not approved to use these commands.")

@app.on_message(filters.command(["imglist", "imagelist"], prefixes=["/", "!"]) & filters.user(OWNER_ID))
async def list_approved_users(client: Client, message: Message):
    # List all approved users
    if not approved_users:
        return await message.reply("ℹ️ No users are currently approved to use /imgs or /image commands.")
    
    user_list = "\n".join([str(user) for user in approved_users])
    await message.reply(f"✅ Approved users:\n{user_list}")
