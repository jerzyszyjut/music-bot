import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
import asyncio
import re


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot("#", intents=intents)

queues = {}


def extract_video_id(url):
    # Define the regex pattern to match YouTube video IDs
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/.*(?:\?|\&)v=|youtu\.be/|.*youtu.be/)([a-zA-Z0-9_-]{11})'
    
    # Use re.search to find the match in the URL
    match = re.search(pattern, url)
    
    # If a match is found, return the video ID
    if match:
        return match.group(1)
    else:
        return None

def download_mp3(youtube_url, output_path=None):
    if output_path is None:
        output_path = extract_video_id(youtube_url) + ".mp3"
    output_path = os.path.join("music", output_path)
    logger.info(f"Downloading {youtube_url} to {output_path}")

    options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': output_path,
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([youtube_url])

    logger.info(f"Downloaded {youtube_url} to {output_path}")

    return output_path

def add_to_queue(guild_id, song_url):
    if guild_id in queues:
        queues[guild_id]["songs"].append(song_url)
    else:
        queues[guild_id] = {"songs": [song_url]}

def remove_from_queue(guild_id, song_number):
    if guild_id in queues:
        del queues[guild_id]["songs"][song_number]
    else:
        queues[guild_id] = {"songs": []}

def clear_queue(guild_id):
    if guild_id in queues:
        queues[guild_id] = []
    else:
        queues[guild_id] = []

def shuffle_queue(guild_id):
    if guild_id in queues:
        queues[guild_id]["songs"] = queues[guild_id]["songs"].shuffle()
    else:
        queues[guild_id] = {"songs": []}


@bot.event
async def on_ready():
    await bot.tree.sync()
    logger.info(f"{bot.user} has connected to Discord!")
    

@bot.command(
  name="play",
  aliases=["p"],
  description="Plays queue",
  usage="play",
)
async def play(ctx):
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client

    # If the bot is not already in a voice channel
    if voice_client is None:
        await voice_channel.connect()
        voice_client = ctx.guild.voice_client
    elif voice_channel != voice_client.channel:
        await voice_client.disconnect()
        await voice_channel.connect()
        voice_client = ctx.guild.voice_client

    while queues[ctx.guild.id]["songs"]:
        song_url = queues[ctx.guild.id]["songs"].pop(0)
        song_path = download_mp3(song_url)
        voice_client.play(discord.FFmpegPCMAudio(song_path))
        while voice_client.is_playing():
            await asyncio.sleep(1)

    await voice_client.disconnect()


@bot.event
async def on_voice_state_update(member, before, after):
    if not member.bot and before.channel and not after.channel:
        if len(before.channel.members) == 1:
            await before.channel.disconnect()

@bot.command(
    name="add",
    aliases=["a"],
    description="Adds a song to the queue",
    usage="add <song_url>",
    )
async def add(ctx, *, song_url):
    add_to_queue(ctx.guild.id, song_url)
    await ctx.send(f"Added {song_url} to the queue")


@bot.command(
    name="leave",
    aliases=["l"],
    description="Leaves the voice channel",
    usage="leave",
    )
async def leave(ctx):
    channel = ctx.guild.voice_client
    await channel.disconnect()
    await ctx.send("I have left the voice channel")

@bot.command(
    name="pause",
    aliases=["pa"],
    description="Pauses the current song",
    usage="pause",
    )
async def pause(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused the current song")
    else:
        await ctx.send("No song is currently playing")

@bot.command(
    name="resume",
    aliases=["r"],
    description="Resumes the current song",
    usage="resume",
    )
async def resume(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed the current song")
    else:
        await ctx.send("No song is currently paused")

@bot.command(
    name="stop",
    aliases=["s"],
    description="Stops the current song",
    usage="stop",
    )
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        await ctx.send("Stopped the current song")
    else:
        await ctx.send("No song is currently playing")

@bot.command(
    name="skip",
    aliases=["sk"],
    description="Skips the current song",
    usage="skip",
    )
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        await ctx.send("Skipped the current song")
    else:
        await ctx.send("No song is currently playing")

@bot.command(
    name="queue",
    aliases=["q"],
    description="Shows the current queue",
    usage="queue",
    )
async def queue(ctx):
    message = ""
    message += "Current queue:\n"
    for i, song in enumerate(queues[ctx.guild.id]["songs"]):
        message += (f"{i+1}. {song}\n")
    await ctx.send(message)

@bot.command(
    name="shuffle",
    aliases=["sh"],
    description="Shuffles the current queue",
    usage="shuffle",
    )
async def shuffle(ctx):
    shuffle_queue(ctx.guild.id)

@bot.command(
    name="clear",
    aliases=["c"],
    description="Clears the current queue",
    usage="clear",
    )
async def clear(ctx):
    clear_queue(ctx.guild.id)

@bot.command(
    name="remove",
    aliases=["rm"],
    description="Removes a song from the queue",
    usage="remove <song_number>",
    )
async def remove(ctx, *, song_number):
    remove_from_queue(ctx.guild.id, song_number)

def main():
    bot.run(TOKEN)
