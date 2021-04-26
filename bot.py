# Bot.py
import os
import discord
from discord.ext import commands, tasks
import logging
import inspect
import pyracing
#import pyracing_bullethell
from dotenv import load_dotenv
from pyracing.client import Client
#from pyracing/bullethell.client import Client
import DiscordUtils
from pyracing import constants
#from pyracing/bullethell import constants
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


    @tasks.loop(seconds=2)
    async def licenseClassChecker():
        print("yeeeeeeeeeeeet")
        
    @commands.command(name="schedule", description="Gets schedule of specified series")
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

        await ctx.send(out)

    @commands.command()
    async def last(ctx,*,driverId=None):
        info={
            "driverName": "", "track": "", "car": "", "iratingChange": 0, "startPos": 0, "finishPos": 0, "incidents": 0
        }
        driver_status = await Client(USERNAME, PASSWORD).driver_status(driverId)
        if len(driver_status)==0:
            embed = discord.Embed(title="Error")
            embed.add_field(name="Input error", value="Looks like there was an error in the imput, if make sure the first letter of first and last name is capitalised")
            await ctx.send(embed=embed)
        else:
            driver_status = driver_status[0]
            lastRaces = await Client(USERNAME, PASSWORD).last_races_stats(driver_status.cust_id)
            eventResults = await Client(USERNAME,PASSWORD).event_results(driver_status.cust_id, quarter=1, show_unofficial=1)
            new = await Client(USERNAME,PASSWORD).subsession_data(lastRaces[0].subsession_id)

            for d in new.drivers:
                if int(d.cust_id) == int(driver_status.cust_id) and d.sim_ses_name == "RACE":
                    info["driverName"] = d.display_name
                    info["track"] = lastRaces[0].track
                    info["car"] = d.car_class_name
                    info["iratingChange"] = d.irating_new-d.irating_old
                    info["startPos"] = eventResults[0].pos_start
                    info["finishPos"] = eventResults[0].pos_finish
                    info["incidents"] = lastRaces[0].incidents

            embed = discord.Embed(title=f"Latest Race Result From  {info['driverName']}")
            embed.add_field(name='Track', value=info["track"])
            embed.add_field(name='Car/Class', value=info["car"])
            embed.add_field(name='Grid Position', value=info["startPos"])
            embed.add_field(name='Finish Position', value=info["finishPos"])
            embed.add_field(name='Iracing Gain/Loss', value=info["iratingChange"])
            embed.add_field(name='Incidents', value=info["incidents"])
            await ctx.reply(embed=embed)


    @commands.command(name='series', description='Gets all series of specified road type')
    async def series(ctx,*, arg=None):
        arg=arg.lower()
        if arg==None:
            embed = discord.Embed(title="Error in input")
            embed.add_field(name='Error', value="Missing series category input \n Usage example !series road")
            await ctx.send(embed=embed)
        elif arg!=None and not arg in SeriesCategories:
            embed = discord.Embed(title="Error in input")
            embed.add_field(name='Error', value="Invalid category\nCategories are road, oval, dirt road and dirt oval")
            await ctx.send(embed=embed)
        else:
            listToConvert=[]
            stringToSend="SR   SERIES NAME\n"         
            seasons_list = await Client(USERNAME, PASSWORD).current_seasons()
            for season in seasons_list:
                if SeriesCategories[season.category-1]==arg:
                    listToConvert.append([season.series_lic_group_id, season.series_name_short])
            listToConvert.sort()
            for x in listToConvert:
                stringToSend+=f"{constants.License(x[0]).name}     {x[1]} \n"
            await ctx.send(stringToSend)

    @commands.command(name='irating', description='Returns irating of specified driver')
    async def irating(ctx, driver, category):
        driver_statuses = await Client(USERNAME,PASSWORD).driver_status(search_terms=driver)

        embed = discord.Embed(title=f'Driver {driver}\'s iRating')

        if len(driver_statuses) != 0:
            driver_status = driver_statuses[0]
            ir = await Client(USERNAME,PASSWORD).irating(
                cust_id=driver_status.cust_id,
                category=constants.Category[category].value
            )
            lc = await Client(USERNAME,PASSWORD).license_class(
                cust_id=driver_status.cust_id,
                category=constants.Category[category].value
            )

            embed.add_field(name='Driver', value=driver_status.name, inline=True)
            embed.add_field(name='iRating', value=ir.current().value, inline=True)
            embed.add_field(
                name='Safety Rating',
                value=f'{lc.current().class_letter()} {lc.current().safety_rating()}',
                inline=True
            )
            embed.add_field(name='Category', value=category, inline=True)
        else:
            embed.add_field(name='Search', value=f'Driver {driver} not found.')
        await ctx.reply(embed=embed)

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
