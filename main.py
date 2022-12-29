import discord
import io
from discord.ext import commands
from discord.commands import Option
from discord.commands import permissions
import random
import threading
import requests
import os
import string
from botLib import *

loginmessage = "Login Required for user"

color_code = [0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F, 0x800000, 0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585, 0xFFB6C1, 0x00CED1]

bot = discord.Bot()

@bot.event
async def on_application_command_error(ctx, error):
    print(error)
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.respond("**{}**".format(error))
    else:
        await ctx.respond("**Unknown Error!**")

@bot.slash_command(description="Pong!")
async def ping(ctx):
  await ctx.defer()
  await ctx.respond("Pong! `{} ms`".format(bot.latency))

@bot.slash_command(description="Show list of commands")
async def help(ctx):
    await ctx.defer()
    embed=discord.Embed()
    embed.set_author(name="Quizizz Tools", icon_url="https://cdn.discordapp.com/avatars/913442195388903467/2aacaa2f10836e4f4814414cedef4fc8.webp?size=160")
    embed.add_field(name="__**Main Commands**__", value="\u200b", inline=False)
    embed.add_field(name="/accountgenerator", value="Generate real quizizz account.", inline=False)
    embed.add_field(name="/addplayer", value="Add player to room.", inline=False)
    embed.add_field(name="/addpowerup", value="Add powerup to player.", inline=False)
    embed.add_field(name="/floodroom", value="Flood quizizz room with bot.", inline=False)
    embed.add_field(name="/getroominfo", value="Get quizizz room info (raw).", inline=False)
    embed.add_field(name="/roomfinder", value="Find a active quizizz room.", inline=False)
    embed.add_field(name="/startgame", value="Force start any quizizz room.", inline=False)
    embed.add_field(name="__**Other Commands**__", value="\u200b", inline=False)
    embed.add_field(name="/vote", value="Check if you vote or not.", inline=False)
    embed.add_field(name="/blacklist", value="Temporary blacklist user from the bot.", inline=False)
    embed.add_field(name="/clearblacklist", value="Clear the blacklist.", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(description="Vote for the bot!")
@commands.cooldown(1, 30, type=commands.BucketType.user)
async def vote(ctx):
    await ctx.defer()
    embed=discord.Embed(title="Vote Status", color=random.choice(color_code))
    embed.add_field(name="Quizizz Tools", value="Click [here](https://top.gg/bot/913442195388903467/vote) to vote for the bot!", inline=True)
    if checkVote(ctx.author.id) == True:
        embed.set_footer(text="You have voted today!")
    elif checkVote(ctx.author.id) == False:
        embed.set_footer(text="You haven't vote today!")
    else:
        embed.set_footer(text="An error occurred while trying to get the value!")
    await ctx.respond(embed=embed)

blacklist = bot.create_group("add", "remove", "clear")
@blacklist.command(description="Add user to the list")
async def add(ctx, userid: str):
  if ctx.author.id != "818856266721132564" and ctx.author.id != 818856266721132564:
    await ctx.respond("You can't use this command :thinking:")
    return
  else:
    try:
      pingchar = ['<', '>', '@', '!']
      userid = ''.join([c for c in userid if c not in pingchar])
      open("blacklist.txt", "a").write(userid + " ")
      await ctx.respond(f"Blacklisted <@{userid}>", allowed_mentions=discord.AllowedMentions.none())
    except:
      await ctx.respond(f"Failed to blacklist <@{userid}>", allowed_mentions=discord.AllowedMentions.none())

@blacklist.command(description="Remove user from the list")
async def remove(ctx, userid: str):
  if ctx.author.id != "818856266721132564" and ctx.author.id != 818856266721132564:
    await ctx.respond("You can't use this command :thinking:")
    return
  else:
    try:
      pingchar = ['<', '>', '@', '!']
      userid = ''.join([c for c in userid if c not in pingchar])
      userids = open("blacklist.txt", "r").read()
      userids = replaceAll(userids, userid, "")
      if userids:
        open("blacklist.txt", "w").write(userid + " ")
        await ctx.respond(f"Remove <@{userid}> from the list.", allowed_mentions=discord.AllowedMentions.none())
      else:
        await ctx.respond(f"Failed to remove <@{userid}> from the list.", allowed_mentions=discord.AllowedMentions.none())
    except:
      await ctx.respond(f"Failed to remove <@{userid}> from the list.", allowed_mentions=discord.AllowedMentions.none())

@blacklist.command(description="Clear the list")
async def clear(ctx):
  if ctx.author.id != "818856266721132564" and ctx.author.id != 818856266721132564:
    await ctx.respond("You can't use this command :thinking:")
    return
  else:
    try:
      open("blacklist.txt", "w").close()
      await ctx.respond("Cleared the list!")
    except:
      await ctx.respond("Failed to clear the list!")

"""
@bot.slash_command(description="Blacklist user!")
async def blacklist(ctx, userid: str):
  if ctx.author.id != "818856266721132564" and ctx.author.id != 818856266721132564:
    await ctx.respond("You can't use this command :thinking:")
    return
  else:
    try:
      pingchar = ['<', '>', '@', '!']
      userid = ''.join([c for c in userid if c not in pingchar])
      open("blacklist.txt", "a").write(userid + " ")
      await ctx.respond(f"Blacklisted <@{userid}>", allowed_mentions=discord.AllowedMentions.none())
    except:
      await ctx.respond(f"Failed to blacklist <@{userid}>", allowed_mentions=discord.AllowedMentions.none())

@bot.slash_command(description="Clear Blacklist")
async def clearblacklist(ctx):
  if ctx.author.id != "818856266721132564" and ctx.author.id != 818856266721132564:
    await ctx.respond("You can't use this command :thinking:")
    return
  else:
    try:
      open("blacklist.txt", "w").close()
      await ctx.respond("Cleared the list!")
    except:
      await ctx.respond("Failed to clear the list!")
"""

@bot.slash_command(description="Add Powerup to player")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def addpowerup(ctx, roomcode: str, name: str, powerup: Option(str, "Choose the powerup", choices=["Double Jeopardy", "X2", "50-50", "Eraser", "Immunity", "Time Freeze", "Power Play", "Streak Saver", "Glitch", "Streak Booster", "Super Sonic", "All"])):
  await ctx.defer()
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    raw_powerup = ""
    if powerup.casefold() == "Double Jeopardy".casefold():
      raw_powerup = "double-jeopardy"
    elif powerup.casefold() == "X2".casefold():
      raw_powerup = "2x"
    elif powerup.casefold() == "50-50".casefold():
      raw_powerup = "50-50"
    elif powerup.casefold() == "Eraser".casefold():
      raw_powerup = "eraser"
    elif powerup.casefold() == "Immunity".casefold():
      raw_powerup = "immunity"
    elif powerup.casefold() == "Time Freeze".casefold():
      raw_powerup = "time-freeze"
    elif powerup.casefold() == "Power Play".casefold():
      raw_powerup = "power-play"
    elif powerup.casefold() == "Streak Saver".casefold():
      raw_powerup = "streak-saver"
    elif powerup.casefold() == "Glitch".casefold():
      raw_powerup = "glitch"
    elif powerup.casefold() == "Streak Booster".casefold():
      raw_powerup = "streak-booster"
    elif powerup.casefold() == "Super Sonic".casefold():
      raw_powerup = "supersonic"
    elif powerup.casefold() == "All".casefold():
      raw_powerup = [
        {
          "name": "2x",
          "meta": {
            "beltPosition": 0,
          }
        },
        {
          "name": "double-jeopardy",
          "meta": {
            "beltPosition": 1,
          }
        },
        {
          "name": "50-50",
          "meta": {
            "beltPosition": 2,
          }
        },
        {
          "name": "immunity",
          "meta": {
            "beltPosition": 3,
          }
        },
        {
          "name": "time-freeze",
          "meta": {
            "beltPosition": 4,
          }
        },
        {
          "name": "power-play",
          "meta": {
            "beltPosition": 5,
          }
        },
        {
          "name": "streak-saver",
          "meta": {
            "beltPosition": 6,
          }
        },
        {
          "name": "glitch",
          "meta": {
            "beltPosition": 7,
          }
        },
        {
          "name": "streak-booster",
          "meta": {
            "beltPosition": 8,
          }
        },
        {
          "name": "supersonic",
          "meta": {
            "beltPosition": 9,
          }
        },
        {
          "name": "eraser",
          "meta": {
            "beltPosition": 10,
          }
        }
      ]
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if not rdata:
      await ctx.respond("**Invaild Quizizz Room Code! Make sure you type correct room code.**", ephemeral=True)
    elif rdata.get('powerups') == 'no':
      await ctx.respond("**This quizizz room has disabled powerup!**")
    else:
      roomhash = rdata.get('hash')
      gtype = rdata.get('type')
      if powerup.casefold() == "All".casefold():
        addpowerup = requests.post('https://game.quizizz.com/play-api/awardPowerups', json={"roomHash": roomhash,"playerId": name,"powerups": raw_powerup,"gameType": gtype})
      else:
        addpowerup = requests.post('https://game.quizizz.com/play-api/awardPowerup', json={"roomHash": roomhash,"playerId": name,"powerup":{"name": raw_powerup},"gameType": gtype})
      if addpowerup.status_code == 200:
        await ctx.respond(f"**Successfully Added that Powerup to `{name}`. If you don't see the powerup, reload the page.**")
      else:
        await ctx.respond("**Failed to add that powerup, are you write correct name?**")

@bot.slash_command(description="Give you a working quizizz account.")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def accountgenerator(ctx):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    email = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=random.randint(8, 10))) + random.choice(['@gmail.com', '@apple.com', '@microsoft.com', '@outlook.com'])
    password = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12))
    firstName = ["Edward", "Robert", "Daniel", "Jack", "John", "David", "Adam"]
    lastName = ["Butler", "Sanders", "Shaw", "Richardson", "Brooks", "Brown", "West", "Cruz", "Gonzales"]
    headers = {
    "accept": "*/*",
    "accept-language": "en",
    "content-type": "application/json",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}
    payload = {
    "title":"",
    "firstName":random.choice(firstName),
    "lastName":random.choice(lastName),
    "password":password,
    "occupation":"other",
    "preferences": {
        "communicationAllowed":True
    },
    "email":email,
    "source": {
            "at":"landing_header"
    }
}
    account = requests.post("https://quizizz.com/_api/landingPg/user/register", headers=headers, json=payload)
    if account.status_code == 201:
      await ctx.respond("Successfully Generated a account, please check your DM!")
      await ctx.author.send(f"""
**Email:** `{email}`
**Password:** ||`{password}`||
""")
    else:
      await ctx.respond("Failed to generate account!")

@bot.slash_command(description="Find an active room on Quizizz.")
@commands.cooldown(1, 10, type=commands.BucketType.user)
async def roomfinder(ctx):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    await ctx.respond("Please wait few seconds so it can found the working code!")
    while True:
      qcode = str(random.randint(100000, 999999))
      response = requests.post(f"https://game.quizizz.com/play-api/v5/checkRoom", json={"roomCode": qcode})
      data2 = response.json()
      if not 'error' in data2:
        await ctx.author.send(f"""**Vaild Room Code: `{qcode}`**
**Room Hash: **`{data2.get('room').get('hash')}`
**Host ID: **`{data2.get('room').get('hostId')}`
      """)
        break
      elif data2.get('error').get('message') == loginmessage:
        await ctx.author.send(f"""**Vaild Room Code: `{qcode}` (Login required for this room)**
**Room Hash: **`{data2.get('room').get('hash')}`
**Host ID: **`{data2.get('room').get('hostId')}`
      """)
        break

@bot.slash_command(description="Flood a quizizz room with BOT!")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def floodroom(ctx, roomcode: str, botamount: int):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    if botamount > 25:
      await ctx.respond("Please add smaller than 25 bots per command!")
      return
    await ctx.respond(f"Adding Bot to room `{roomcode}`")
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if not rdata:
      await ctx.respond("Invaild Room Code!", ephemeral=True)
    else:
      roomhash = rdata.get('hash')
      for i in range(botamount):
        fakeip = f"{str(random.randint(100, 255))}.{str(random.randint(100, 255))}.{str(random.randint(100, 255))}.{str(random.randint(100, 255))}"
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        addbot = requests.post("https://game.quizizz.com/play-api/v5/join", json={"roomHash": roomhash, "player":{"id": name, "origin": "web", "isGoogleAuth": False, "avatarId": random.randint(1, 10)}, "__cid__":"v5/join.|1.1632599434062", "ip": fakeip})
    await ctx.author.send(f"Successfully Added {i+1} Bots to `{roomcode}`")

@bot.slash_command(description="Get Room Info By Room Code")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def getroominfo(ctx, roomcode: str):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    if not room.json().get("room"):
      await ctx.respond("Invaild Room Code!", ephemeral=True)
    else:
      await ctx.respond(" ", file=discord.File(io.StringIO(str(room.json())), "info.json"))

@bot.slash_command(description="Add Player to room")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def addplayer(ctx, roomcode: str, playername: str):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if rdata:
      roomhash = rdata.get('hash')
      fakeip = f"{str(random.randint(100, 255))}.{str(random.randint(100, 255))}.{str(random.randint(100, 255))}.{str(random.randint(100, 255))}"
      addbot = requests.post("https://game.quizizz.com/play-api/v5/join", json={"roomHash": roomhash, "player":{"id": playername, "origin": "web", "isGoogleAuth": False, "avatarId": random.randint(1, 10)}, "__cid__":"v5/join.|1.1632599434062", "ip": fakeip})
      if addbot.status_code == 200:
        await ctx.respond(f"Added `{playername}` to `{roomcode}`")
      else:
        await ctx.respond("Failed to add player to room!", ephemeral=True)
    else:
      await ctx.respond("Invaild Room Code!", ephemeral=True)
        
"""
@bot.slash_command(description="Force Start ANY quizizz game.")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def startgame(ctx, roomcode: str):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if rdata == None:
      await ctx.respond("Invaild Room Code!", ephemeral=True)
    else:
      roomhash = rdata.get('hash')
      start = requests.post("https://quizizz.com/_api/main/game/start", json={"roomHash": roomhash})
      if start.status_code == 200:
        await ctx.respond("Started the game!")
      else:
        await ctx.respond("Failed to start the game!")

@bot.slash_command(description="Force End ANY quizizz game.")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def endgame(ctx, roomcode: str):
  if checkBlacklist(str(ctx.author.id)) == True:
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
    return
  else:
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if rdata == None:
      await ctx.respond("Invaild Room Code!", ephemeral=True)
    else:
      roomhash = rdata.get('hash')
      end = requests.post("https://quizizz.com/_api/main/game/pause", json={"pauseFor": 0,"roomHash": roomhash})
      if end.status_code == 200:
        await ctx.respond("Ended the game!")
      else:
        print(end.json())
        await ctx.respond("Failed to end the game!")
"""

@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help | {} servers!".format(str(len(bot.guilds)))), status=discord.Status.online)
  print("Logged in as {0.user}".format(bot))

bot.run(os.environ['BOT_TOKEN'])
