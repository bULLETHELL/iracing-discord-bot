# Bot.py
import os
import discord
import logging
from dotenv import load_dotenv

# Discord Bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Client Class
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")

client = MyClient()
client.run(TOKEN)
