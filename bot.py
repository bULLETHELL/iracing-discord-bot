# Bot.py
import os
import discord
from discord.ext import commands
import logging
import inspect
import pyracing
from dotenv import load_dotenv
from pyracing.client import Client
import DiscordUtils
#Global Variables
SeriesCategories = ['oval', 'road', 'dirt oval', 'dirt road']
LicenseClasses = ['R', 'D', 'C','B','A']
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
    async def schedule(ctx, *, arg=None):
        seasons_list = await Client(USERNAME, PASSWORD).current_seasons()

        if arg is None:
            embed = discord.Embed(title='Usage: !schedule {series_name}')
        else:
            for season in seasons_list:
                if season.series_name_short == arg:
                    embed = discord.Embed(title=f'Schedule for {season.series_name_short} ({season.season_year} S{season.season_quarter})')
                    for t in season.tracks:
                        embed.add_field(name=f'Week {t.race_week+1}', value=f'{t.name} ({t.config})', inline=True)
                    break
                else:
                    embed = discord.Embed(title=f'{arg} isn\'t a valid series name.')
        # Pagination
        #if len(out) // 2000 == 1:
        #    for n in range((len(out)//2000)):
        #        print("xd")
        #else:
        await ctx.send(embed=embed)

    @commands.command()
    async def series(ctx,*, arg=None):
        if arg==None:
            ctx.send("Error: missing series category input \n Usage example !series road")
        elif arg!=None and not arg in SeriesCategories:
            await ctx.send("Error, invalid category\nCategories are road, oval, dirt road and dirt oval")
        else:
            listToConvert=[]
            stringToSend=""         
            seasons_list = await Client(USERNAME, PASSWORD).current_seasons()
            for season in seasons_list:
                if SeriesCategories[season.category-1]==arg:
                    listToConvert.append([season.series_lic_group_id, season.series_name_short])
            listToConvert.sort()
            for x in listToConvert:
                stringToSend+=f"{LicenseClasses[x[0]-1]} {x[1]} \n"
            await ctx.send(stringToSend)
    
    @commands.command()
    async def paginate(ctx):
        embed1 = "hello"
        embed2 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 2")
        embed3 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 3")
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = [embed1, embed2, embed3]
        await paginator.run(embeds)

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
