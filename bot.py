import os
import asyncio
import discord
from discord.ext import commands
import youtube_dl

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'extract_flat': False,
    'default_search': 'ytsearch',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)

async def join_channel(ctx):
    if ctx.author.voice is None:
        await ctx.send('You are not connected to a voice channel.')
        return False
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
    return True

@bot.command()
async def play(ctx, *, url: str):
    if not await join_channel(ctx):
        return
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    if 'entries' in data:
        data = data['entries'][0]
    source = discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS)
    ctx.voice_client.play(source)
    await ctx.send(f"Now playing: {data.get('title')}")

@bot.command()
async def pause(ctx):
    if ctx.voice_client is not None:
        ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    if ctx.voice_client is not None:
        ctx.voice_client.resume()

@bot.command()
async def stop(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('Please set the DISCORD_TOKEN environment variable.')
    else:
        bot.run(token)
