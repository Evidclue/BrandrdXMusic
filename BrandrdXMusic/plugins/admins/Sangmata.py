import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory

# Import your userbot and assistants setup
from BrandrdXMusic import userbot as us, app
from BrandrdXMusic.core.userbot import assistants

@app.on_message(filters.command("sg"))
async def sg(client: Client, message: Message):
    # Check if message contains the required parameters
    if len(message.text.split()) < 1 and not message.reply_to_message:
        return await message.reply("sg username/id/reply")
    
    # If it's a reply, get the user id from the reply; else, get from the text
    if message.reply_to_message:
        args = message.reply_to_message.from_user.id
    else:
        args = message.text.split()[1]

    lol = await message.reply("<code>Processing...</code>")
    
    # Fetch the user
    if args:
        try:
            user = await client.get_users(f"{args}")
        except Exception:
            return await lol.edit("<code>Please specify a valid user!</code>")
    
    # Choose the bot to interact with randomly
    bo = ["sangmata_bot", "sangmata_beta_bot"]
    sg = random.choice(bo)

    # Assuming assistants contains your userbot instances, use the first one
    if 1 in assistants:
        ubot = us.one  # Ensure `us.one` is the correct reference to the userbot client instance

    try:
        # Send user ID to the selected bot and delete the message
        a = await ubot.send_message(sg, f"{user.id}")
        await a.delete()
    except Exception as e:
        return await lol.edit(f"<code>{e}</code>")

    # Give time for message processing and check the bot's response
    await asyncio.sleep(1)

    # Search for the bot's messages and extract the response
    async for stalk in ubot.search_messages(a.chat.id):
        if stalk.text == None:
            continue
        if not stalk:
            await message.reply("Bot is unresponsive")
        elif stalk:
            await message.reply(f"Response from bot: {stalk.text}")
            break  

    try:
        # Try resolving the bot's peer and delete history
        user_info = await ubot.resolve_peer(sg)
        await ubot.send(DeleteHistory(peer=user_info, max_id=0, revoke=True))
    except Exception as e:
        pass
    
    # Delete the processing message after completion
    await lol.delete()
