# Bot.py
import os
import discord
from discord.ext import commands
import logging
import inspect
import pyracing
from dotenv import load_dotenv
from pyracing.client import Client

# Discord Bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
USERNAME = os.getenv('IRACING_USERNAME')
PASSWORD = os.getenv('IRACING_PASSWORD')

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Bot Class
class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix='!')
        
        # Add commands to self
        members = inspect.getmembers(self)
        for name, member in members:
            if isinstance(member, commands.Command):
                if member.parent is None:
                    self.add_command(member)

    @commands.command()
    async def test(ctx):
        await ctx.send('test successful')

    @commands.command()
    async def schedule(ctx, *, arg=None):
        seasons_list = await Client(USERNAME, PASSWORD).current_seasons()
        out = ''

        if arg is None:
            out = f'{ctx.author.mention}\nUsage: !schedule "series_name"'
        else:
            for season in seasons_list:
                if season.series_name_short == arg:
                    out = f'{ctx.author.mention}\nSchedule for {season.series_name_short} ({season.season_year} S{season.season_quarter})\n'
                    for t in season.tracks:
                        out += f'\tWeek {t.race_week+1} will take place at {t.name} ({t.config})\n'
                    break
                else:
                    out = f'{ctx.author.mention}\n"{arg}" isn\'t a valid series name.'

        await ctx.send(out)

    def run(self):
        super().run(TOKEN)

if __name__ == "__main__":
    bot = Bot()
    bot.run()

# Client Class
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")

client = MyClient()
client.run(TOKEN)
