from gc import enable
import discord, pytz, json, os, datetime
from discord import activity
from discord.embeds import Embed
from discord.ext import commands, tasks
from discord.ext.commands.errors import NotOwner
import requests as req
from dateutil import parser

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Prefix": "!"}
    
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]
prefix = configData["Prefix"]

#Global Variables
addminute = 0
drawdate = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
drawid = 0

bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print('Bot is ready')


@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f"Pong! {latency}")


@tasks.loop(minutes=1)
async def getwinners(ctx, winnersinterval):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    global drawdate
    global drawid
    id = drawid
    global addminute
    date = drawdate + datetime.timedelta(minutes=winnersinterval)
    print(date)
    if(date.day == now.day and date.hour == now.hour and date.minute == (winnersinterval + addminute)):
        print('Fetching winners...')
        url = 'https://delo-stats.azurewebsites.net/api/previous-winners?code=WDWAXx2Od/VCGwRz6qnXyNKkX4YJHWN3yWVPD7rWfKaqum6gKYW4RQ=='
        PARAMS = {'id': id}
        response = req.get(url=url, params=PARAMS)
        res = response.json()
        winners = res['winners']
        if not winners:
            print('Draw has not ended yet...')
            print('Retrying after 1 minute...\n')
            addminute += 1
        else:
            print('Draw Winners!!!\n')
            await postwinners(ctx, res)


async def postwinners(ctx, res):
    channel = bot.get_channel(915738766839271444)
    id = res['id']
    jackpot = res['jackpotUSD']
    winners = res['winners']
    positions = ''
    usdamt = ''
    deloamt = ''
    address = ''
    numwinners = 0
    for winner in winners:
        address += str(winner['address'] + '\n')
        usdamt += str(winner['usdAmount'] + '\n')
        deloamt += str(winner['deloAmount'] + '\n')
        for pos in winner['positions']:
            positions += str(pos) + ','
            numwinners += 1
        positions += '\n'

    embed = discord.Embed(title="Congratulations to this Draws lucky Winners!")
    embed.add_field(name='Draw No ', value=id, inline=True)
    embed.add_field(name='Jackpot ', value=jackpot, inline=True)
    embed.add_field(name='Winners: ', value=numwinners, inline=True) 
    embed.add_field(name='Positions', value=positions, inline=True)    
    embed.add_field(name='USD', value=usdamt, inline=True)
    embed.add_field(name='Address', value=address, inline=True)
    print(res)
    await channel.send(embed=embed)
       
@bot.command()
async def jackbot(ctx, enabled="start", potinterval=10, winnersinterval=5):
    if enabled.lower() == "stop":
        fetchJackpot.stop()
        getwinners.stop()
    elif enabled.lower() == "start":
        fetchJackpot.change_interval(seconds=int(potinterval))
        fetchJackpot.start(ctx)
        getwinners.start(ctx, winnersinterval)


@tasks.loop(seconds=10)
async def fetchJackpot(ctx):
    guild = ctx.guild
    global drawid
    global drawdate
    response = req.get('https://delo-stats.azurewebsites.net/api/lotto-stats?code=yeIblDu0vazoxpQ9Bcv03P35vyjAHh0izlyojw635IS1tkO6aoMCSQ==')
    res = response.json()
    id = res['id']
    jackpot = res['totalPot']
    nickname = "[!] JackBot: %s"%jackpot
    tickets = res['numTickets']
    winners = res['numParticipants']
    deadline = res['drawDeadline']
    drawdate = parser.parse(deadline)
    drawdate = drawdate.replace(tzinfo=pytz.UTC)
    activity = 'Tickets: %s, Winners: %s, Draw Date: %s' % (tickets, winners, deadline)
    drawid = id
  
    await guild.me.edit(nick=nickname)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
    print('Draw Id: %s, Draw Date: %s' % (drawid, drawdate))
    print('Jakcpot: %s, Tickets: %s,  Winners: %s \n' %(jackpot, tickets, winners))


bot.run(token)

