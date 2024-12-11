import yt_dlp
import random
import requests
import time
from pyrogram import Client, filters
from pyrogram.errors import ChannelInvalid, PeerIdInvalid
from pyrogram.enums import ChatMemberStatus

# Add your proxy list
PROXY_LIST = [
    'http://123.123.123.123:8080',
    'http://234.234.234.234:8080',
    'http://345.345.345.345:8080',
    # Add more proxies...
]

# Function to fetch a new proxy from the list
def get_new_proxy():
    """Get a random proxy from the list"""
    return random.choice(PROXY_LIST)

# Function to test if a proxy is working
def test_proxy(proxy):
    """Test if the proxy is working by making a request to YouTube"""
    url = 'https://www.youtube.com'  # Check YouTube to verify proxy is working
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to download video with proxy rotation
def download_video_with_proxies(url):
    current_proxy = get_new_proxy()  # Initial proxy
    while True:
        print(f"Trying proxy: {current_proxy}")
        
        # Check if the proxy is working
        if test_proxy(current_proxy):
            print(f"Using proxy: {current_proxy}")
            
            # Set the proxy in yt-dlp options
            ydl_opts = {
                'proxy': current_proxy,  # Set proxy for yt-dlp
                'cookies': 'path/to/cookies.txt',  # Use your cookies file
                'format': 'bestaudio/best',  # Download the best audio
            }
            
            try:
                # Download the video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print("Download completed successfully.")
                break  # Exit loop if download is successful
            except Exception as e:
                print(f"Error during download: {e}")
                if '403 Forbidden' in str(e) or '429 Too Many Requests' in str(e):
                    print("IP is blocked! Switching to a new proxy.")
                    # Rotate proxy and try again
                    current_proxy = get_new_proxy()
                    time.sleep(5)  # Wait before retrying to avoid excessive requests
        else:
            print(f"Proxy {current_proxy} is not working. Trying another one.")
            current_proxy = get_new_proxy()
            time.sleep(5)  # Wait before retrying to avoid excessive requests

# Now integrate this logic into your bot's download handler:

class Hotty(Client):
    def __init__(self):
        super().__init__(
            name="BrandrdXMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        print("Bot started successfully.")

    async def stop(self):
        await super().stop()
        print("Bot stopped.")

    @Client.on_message(filters.command('download'))
    async def download_video(self, message):
        # Get URL from the message
        url = message.text.split(" ")[1]  # Assuming the format is /download <url>
        if not url:
            await message.reply("Please provide a valid YouTube URL.")
            return

        try:
            # Call the download function with proxy rotation
            download_video_with_proxies(url)
            await message.reply("Video download started successfully.")
        except Exception as e:
            await message.reply(f"Failed to download the video. Error: {str(e)}")

# Run the bot
bot = Hotty()
bot.run()