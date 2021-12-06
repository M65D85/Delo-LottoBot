from gc import enable
import discord
from discord import activity
from discord.ext import commands, tasks
import requests as req

import json
import os

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Prefix": "!"}
    
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]
prefix = configData["Prefix"]

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print('Bot is ready')

@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f"Pong! {latency}")

@bot.command()
async def getpot(ctx, enabled="start", interval=10):
    guild = ctx.guild
    if enabled.lower() == "stop":
        fetchJackpot.stop()
    elif enabled.lower() == "start":
        fetchJackpot.change_interval(seconds=int(interval))
        fetchJackpot.start(guild)

@tasks.loop(seconds=10)
async def fetchJackpot(guild):
    response = req.get('https://delo-stats.azurewebsites.net/api/lotto-stats?code=yeIblDu0vazoxpQ9Bcv03P35vyjAHh0izlyojw635IS1tkO6aoMCSQ==')
    res = response.json()
    jackpot = res['totalPot']
    nickname = "[!] JackBot: %s"%jackpot

    tickets = res['numTickets']
    participants = res['numParticipants']
    deadline = res['drawDeadline']
    activity = 'Tickets: %s, Winners: %s, Draw Date: %s' % (tickets, participants, deadline)
    await guild.me.edit(nick=nickname)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
    print(jackpot)

bot.run(token)

