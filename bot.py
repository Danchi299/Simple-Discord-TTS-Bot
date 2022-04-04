print("Loading...")

#Discord
import discord
import discord.utils
from discord.ext import commands
from discord.ext import tasks

#Dependencies
import os
import pyttsx3

#Load Token From .env For Easy Running
try: os.environ['TOKEN']
except: import dotenv ; dotenv.load_dotenv()

#-------------------------------------------------------------------------------------------

#Variables

prefix = '!'
bot = commands.Bot(command_prefix = prefix)

global engine

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty("rate", 120) # TTS Speed
engine.setProperty('voice', voices[2].id)# TTS Voice

bot.queue = []
bot.queueing = 0
bot.read_channel = 0

#-------------------------------------------------------------------------------------------

#Functions

def queue_player(ctx):
    
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    if voice and voice.is_connected():
        if bot.queue:
            engine.save_to_file(bot.queue[0], 'tts.mp3')
            engine.runAndWait()
            try: voice.play(discord.FFmpegPCMAudio('tts.mp3', **{'before_options': '-channel_layout mono', 'options': ['-vn', '-loglevel panic']}), after = lambda e: After(ctx))
            except Exception as e: print(e); After(ctx)
        else: bot.queueing = 0
    else:
        print('Not Connected To Voice Channel')
        bot.queue.pop(0)
        bot.queueing = 0
        

def After(ctx):
    bot.queue.pop(0)
    queue_player(ctx)

def play_queue(ctx):
    if not bot.queueing:
        bot.queueing = 1
        queue_player(ctx)

    
    

#-------------------------------------------------------------------------------------------

#Commands

@bot.command()
async def join(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
  if voice and voice.is_connected(): await voice.disconnect()
  
  if ctx.author.voice: voice = ctx.author.voice.channel
  else: voice = 0

  if voice:
    await voice.connect()
    await ctx.channel.send(f"Joined {voice}")
  else: await ctx.channel.send("You Are Not In A Voice Channel")

@bot.command()
async def leave(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if voice and voice.is_connected(): await voice.disconnect()
  else: await ctx.channel.send("Not Connected To Voice Channel")

@bot.command()
async def tts(ctx, num: int = 1):

  if num:
    bot.read_channel = ctx.channel
    await ctx.send("TTS ON")

  else:
    bot.read_channel = 0
    await ctx.send(f"TTS OFF in {ctx.channel}")


#-------------------------------------------------------------------------------------------

#Events

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(ctx):
  if not ctx.author.bot:
      if ctx.content[0] != prefix and ctx.content != None and ctx.channel == bot.read_channel:
        if discord.utils.get(bot.voice_clients, guild=ctx.guild):
          bot.queue.append(ctx.content)
          play_queue(ctx)
                    
        else:
          await ctx.channel.send('Not Connected To Voice Chat\nTurning OFF TTS')
          bot.read_channel = 0

      await bot.process_commands(ctx)

#-------------------------------------------------------------------------------------------
    
bot.run(os.environ['TOKEN'])