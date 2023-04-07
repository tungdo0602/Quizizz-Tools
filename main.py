import discord
import io
import random
import requests
import os
import string
import time
import datetime
import asyncio
import threading
from discord.ext import commands
from discord.commands import Option, permissions
from datetime import datetime

loginmessage = "Login Required for user"

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)

def checkBlacklist(userId):
  with open("blacklist.txt") as blacklist:
      if str(userId) in blacklist.read():
          return True
      else:
          return False

def replaceAll(str, char, rechar):
  newstr = str.replace(char, rechar)
  if newstr == str: return False
  else: return newstr

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.respond(embed=discord.Embed(title="Woah, slow down!", description="You can use this command <t:{}:R>".format(int(time.time() + error.retry_after))))
    else:
        await ctx.respond(embed=discord.Embed(title="Unknown Error ¯\_(ツ)_/¯", description="```\n" + str(error) + "\n```"))

def createHelpPage(pageNum=0):
  helpData = {
    "Cheat Commands": {
      "</accountgenerator:948197452685672508>": "Generate quizizz account.",
      "</addplayer:950656396444172338>": "Add player to room.",
      "</addpowerup:928500685102776352>": "Add powerup to player.",
      "</getroominfo:958753737600536616>": "Export room info.",
      "</roomfinder:928500685102776353>": "Find a active Quizizz room.",
      "</spamreaction:1078358844771668058>": "Spam reaction."
    },
    "Other Commands": {
      "</vote:960884315477123163>": "Vote for the bot.",
      "</help:963096500848697384>": "Show help.",
      "</invites:1065500914183569470>": "Invite stuffs.",
      "</ping:981358400568975440>": "Pong!"
    },
    "Owner Commands": {
      "/blacklist": "Blacklist manager."
    }
  }
  pageNum = pageNum % len(list(helpData))
  title = list(helpData)[pageNum]
  embed = discord.Embed(title=title)
  for i in list(helpData[title]):
    embed.add_field(name=i, value=helpData[title][i], inline=False)
  embed.set_footer(text=f"Page {pageNum+1} of {len(list(helpData))}")
  return embed

class helpObject(discord.ui.View):
  
  def __init__(self, author: discord.User, alt_res: discord.InteractionResponse):
    super().__init__(timeout=120)
    self.currentPage = 0
    self.author = author
    self.alt_res = alt_res
  
  async def interaction_check(self, interaction) -> bool:
    if interaction.user != self.author:
      await interaction.response.send_message("This is not for you!", ephemeral=True)
      return False
    else:
      return True
  
  async def on_timeout(self):
    for i in self.children:
      i.disabled = True
    embed = createHelpPage(self.currentPage)
    embed.set_footer(text="Timeout exceeded!")
    sentmsg = self.message or self.alt_res
    await sentmsg.edit(embed=embed, view=self)
  
  @discord.ui.button(label="<", style=discord.ButtonStyle.green)
  async def pre_callback(self, button, interaction):
    self.currentPage -= 1
    await interaction.response.edit_message(embed=createHelpPage(self.currentPage))
    
  @discord.ui.button(label=">", style=discord.ButtonStyle.green)
  async def next_callback(self, button, interaction):
    self.currentPage += 1
    await interaction.response.edit_message(embed=createHelpPage(self.currentPage))
    
@bot.slash_command(description="Show list of commands")
async def help(ctx):
  await ctx.defer()
  await ctx.respond(embed=createHelpPage(), view=helpObject(author=ctx.author, alt_res=ctx))    

@bot.slash_command(description="Pong!")
async def ping(ctx):
  await ctx.defer()
  embed = discord.Embed(title=" ", color=discord.Color.random())
  embed.set_author(name="Pong!")
  embed.add_field(name="Latency", value="`{} ms`".format(bot.latency), inline=True)
  embed.set_footer(text=str(datetime.now()))
  await ctx.respond(embed=embed)

blacklist = bot.create_group("blacklist", "Blacklist manager command")
@blacklist.command(description="Add user to the list")
async def add(ctx, userid: str):
  await ctx.defer(ephemeral=True)
  if str(ctx.author.id) != "818856266721132564":
    await ctx.respond("You can't use this command :thinking:")
  else:
    try:
      pingchar = ['<', '>', '@', '!']
      userid = ''.join([c for c in userid if c not in pingchar])
      open("blacklist.txt", "a").write(userid + " ")
      await ctx.respond(f"Added <@{userid}> to the list!", allowed_mentions=discord.AllowedMentions.none())
    except:
      await ctx.respond(f"Failed to add <@{userid}> to the list!", allowed_mentions=discord.AllowedMentions.none())

@blacklist.command(description="Remove user from the list")
async def remove(ctx, userid: str):
  await ctx.defer(ephemeral=True)
  if str(ctx.author.id) != "818856266721132564":
    await ctx.respond("You can't use this command :thinking:")
  else:
    try:
      pingchar = ['<', '>', '@', '!']
      userid = ''.join([c for c in userid if c not in pingchar])
      userids = replaceAll(open("blacklist.txt", "r").read(), userid, "")
      if userids:
        open("blacklist.txt", "w").write(userid + " ")
        await ctx.respond(f"Remove <@{userid}> from the list!", allowed_mentions=discord.AllowedMentions.none())
      else:
        await ctx.respond(f"<@{userid}> isn't in the list!", allowed_mentions=discord.AllowedMentions.none())
    except:
      await ctx.respond(f"Failed to remove <@{userid}> from the list!", allowed_mentions=discord.AllowedMentions.none())

@blacklist.command(description="Clear the list")
async def clear(ctx):
  await ctx.defer(ephemeral=True)
  if str(ctx.author.id) != "818856266721132564":
    await ctx.respond("You can't use this command :thinking:")
  else:
    try:
      open("blacklist.txt", "w").close()
      await ctx.respond("Cleared the list!")
    except:
      await ctx.respond("Failed to clear the list!")

@blacklist.command(description="View the list")
async def view(ctx):
  await ctx.defer(ephemeral=True)
  if str(ctx.author.id) != "818856266721132564":
    await ctx.respond("You can't use this command :thinking:")
  else:
    try:
      users = open("blacklist.txt", "r").read()
      await ctx.respond(" ", file=discord.File(io.StringIO(str(users)), "ids.txt"))
    except:
      await ctx.repsond("Failed to get the list!")

@bot.slash_command(description="Add Powerup to player")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def addpowerup(ctx, roomcode: str, name: str, powerup: Option(str, "Choose the powerup", choices=["Double Jeopardy", "X2", "50-50", "Eraser", "Immunity", "Time Freeze", "Power Play", "Streak Saver", "Glitch", "Streak Booster", "Super Sonic", "All"])):
  await ctx.defer(ephemeral=True)
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
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
      await ctx.respond("**Invaild Quizizz Room Code! Make sure you type correct room code.**")
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
        await ctx.respond("**Failed to add that powerup, are you enter the correct name?**")

@bot.slash_command(description="Give you a working quizizz account.")
@commands.cooldown(1, 60, type=commands.BucketType.user)
async def accountgenerator(ctx):
  await ctx.defer(ephemeral=True)
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
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
      await ctx.respond(f"""
**Email:** `{email}`
**Password:** ||`{password}`||
""")
    else:
      await ctx.respond("Failed to generate account!")

@bot.slash_command(description="Find an active room on Quizizz.")
@commands.cooldown(1, 30, type=commands.BucketType.user)
async def roomfinder(ctx):
  await ctx.defer(ephemeral=True)
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
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

@bot.slash_command(description="Export room info")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def getroominfo(ctx, roomcode: str):
  await ctx.defer(ephemeral=True)
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**", ephemeral=True)
  else:
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    if not room.json().get("room"):
      await ctx.respond("Invaild Room Code!")
    else:
      await ctx.respond(" ", file=discord.File(io.StringIO(str(room.json())), "info.json"))

@bot.slash_command(description="Add player to room")
@commands.cooldown(1, 10, type=commands.BucketType.user)
async def addplayer(ctx, roomcode: str, playername: str = "", amount: int = 1):
  await ctx.defer(ephemeral=True)
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
  else:
    success = 0
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if rdata:
      roomhash = rdata.get('hash')
      for i in range(amount):
        playername = playername or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        fakeip = f"{str(random.randint(100, 255))}.{str(random.randint(100, 255))}.{str(random.randint(100, 255))}.{str(random.randint(100, 255))}"
        addbot = requests.post("https://game.quizizz.com/play-api/v5/join", json={"roomHash": roomhash, "player":{"id": playername + str(i), "origin": "web", "isGoogleAuth": False, "avatarId": random.randint(1, 10)}, "__cid__":"v5/join.|1.1632599434062", "ip": fakeip})
        if addbot.status_code == 200:
          success += 1
      await ctx.respond(f"Successfully Added {success} Bots to `{roomcode}`")
    else:
      await ctx.respond("Invaild Room Code!")
      
@bot.slash_command(description="Spam Reaction")
async def spamreaction(ctx, roomcode: str, playerid: str, reaction: Option(str, "Reactions", choices=["Flexed", "Sup?", "Finger Heart", "Blue Circle", "Sleepy", "Bruh", "uwu", "Once More", "SUS", "Mindblow", "OP", "Among Us", "GG", "IDK how to call this"]), intensity: int = 1, amount: int = 1):
  await ctx.defer(ephemeral=True)
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
  else:
    room = requests.post('https://game.quizizz.com/play-api/v5/checkRoom', json={"roomCode": roomcode})
    rdata = room.json().get('room')
    if rdata:
      def react(h,o,p,r,i):
        return requests.post("https://quizizz.com/play-api/reactionUpdate", json={
            "hostId": o,
            "playerId": p,
            "questionId": "",
            "reactionDetail": {
              "id": r,
              "intensity": i,
            },
            "roomHash": h,
            "triggerType": "live-reaction"
          })
      roomhash = rdata.get('hash')
      hostid = rdata.get('hostId')
      reactions = {
        "Flexed": 1,
        "Sup?": 2,
        "Finger Heart": 3,
        "Blue Circle": 4,
        "Sleepy": 5,
        "Bruh": 6,
        "uwu": 7,
        "Once More": 8,
        "SUS": 9,
        "Mindblow": 10,
        "OP": 11,
        "Among Us": 12,
        "GG": 13,
        "IDK how to call this": 14
      }
      if amount > 50:
        await ctx.respond("You cannot react over 50 emoji per command. Please try again!")
      else:
        await ctx.respond("Running... Please check the dashboard!")
        for _ in range(amount):
          threading.Thread(target=react, args=(roomhash, hostid, playerid, reactions[reaction], intensity)).start()
          await asyncio.sleep(0.1)


"""
@bot.slash_command(description="Force Start ANY quizizz game.")
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def startgame(ctx, roomcode: str):
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
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
  if checkBlacklist(str(ctx.author.id)):
    await ctx.respond("**You're currently in the blacklist, you can't use any command except someone clears the blacklist.**")
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
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="/help with {} servers!".format(str(len(bot.guilds)))), status=discord.Status.online)
  print("Logged in as {0.user}".format(bot))

bot.run(os.environ['BOT_TOKEN'])
