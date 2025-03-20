import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import requests
import yt_dlp
import asyncio
import wikipediaapi
import random
from datetime import datetime
from deep_translator import GoogleTranslator

# Load .env file
load_dotenv()

# Retrieve bot token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("ERROR: Discord bot token is missing! Check your .env file.")

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True 

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot ready event
@bot.event
async def on_ready():
    print(f"✅ DizBot is online as {bot.user}")

# Say hello command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! 👋")

# Kick user command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member.mention} - Reason: {reason}")

# Ban user command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member.mention} - Reason: {reason}")

# Mute user command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)
    await member.add_roles(role)
    await ctx.send(f"🔇 Muted {member.mention}")

# Fetch a meme command
@bot.command()
async def meme(ctx):
    """Fetches a random meme from an API and sends it."""
    try:
        response = requests.get("https://meme-api.com/gimme")
        data = response.json()

        if "url" in data:
            meme_url = data["url"]
            await ctx.send(meme_url)
        else:
            await ctx.send("❌ Couldn't fetch a meme. Try again later!")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# Weather command
@bot.command()
async def weather(ctx, *, city: str):
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        await ctx.send("⚠️ API key is missing! Please check your configuration.")
        return
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") == 200:
        temp = response["main"]["temp"]
        weather_desc = response["weather"][0]["description"]
        city_name = response["name"]
        await ctx.send(f"🌤 The weather in **{city_name}** is **{weather_desc}** with a temperature of **{temp}°C**.")
    else:
        error_message = response.get("message", "Unknown error occurred")
        await ctx.send(f"❌ City not found! ({error_message}) Try again.")

# Join voice channel command (Fixed)
@bot.command()
async def join(ctx):
    """Bot joins the voice channel of the user"""
    if ctx.author.voice:  # Check if user is in a voice channel
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)  # Move bot if already in a channel
        else:
            await channel.connect()
        await ctx.send(f"🎵 Joined {channel.name}")
    else:
        await ctx.send("❌ You need to be in a voice channel first!")

# Leave voice channel command
@bot.command()
async def leave(ctx):
    """Bot leaves the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")
    else:
        await ctx.send("❌ I'm not in a voice channel!")

# Play YouTube audio command (Fixed)
@bot.command()
async def play(ctx, url):
    """Plays a YouTube video audio in a voice channel"""
    
    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel first!")
        return

    # Make sure the bot is in a voice channel
    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        await channel.connect()

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info["url"]

        vc = ctx.voice_client
        ffmpeg_options = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
        vc.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))
        
        await ctx.send(f"🎶 Now playing: **{info['title']}**")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# Stop the bot from playing audio
@bot.command()
async def stop(ctx):
    """Stops playing audio"""
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped playing audio.")
    else:
        await ctx.send("❌ No audio is playing.")

@bot.command()
async def joke(ctx):
    """Sends a random joke."""
    response = requests.get("https://official-joke-api.appspot.com/random_joke").json()
    setup = response["setup"]
    punchline = response["punchline"]
    await ctx.send(f"😂 **{setup}** \n||{punchline}||")


@bot.command()
async def eightball(ctx, *, question: str):
    """Answers a yes/no question."""
    responses = [
        "Yes!", "No!", "Maybe...", "Definitely!", "I don't think so.", 
        "Absolutely!", "Try again later.", "I have no idea."
    ]
    await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command()
async def roll(ctx):
    """Rolls a dice (1-6)."""
    number = random.randint(1, 6)
    await ctx.send(f"🎲 You rolled a {number}!")

@bot.command()
async def fact(ctx):
    """Sends a random fun fact."""
    response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en").json()
    fact = response["text"]
    await ctx.send(f"🤓 Did you know? {fact}")

@bot.command()
async def time(ctx):
    """Shows the current time."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"🕒 Current Time: {now}")

@bot.command()
async def translate(ctx, lang: str, *, text: str):
    """Translates text to a given language."""
    try:
        translation = GoogleTranslator(source="auto", target=lang).translate(text)
        await ctx.send(f"🔤 **Translation:** {translation}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def wiki(ctx, *, query: str):
    """Fetches a short Wikipedia summary."""
    user_agent = "DizBot/1.0 (https://github.com/your-github-repo)"
    wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language="en")

    page = wiki_wiki.page(query)

    if page.exists():
        summary = page.summary[:500] + "..."  # Limit summary length
        await ctx.send(f"📖 **Wikipedia Summary for {query}**:\n{summary}\nRead more: {page.fullurl}")
    else:
        await ctx.send(f"❌ No Wikipedia page found for **{query}**.")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Shows user profile info."""
    member = member or ctx.author  # Default to the command user if no member is mentioned

    embed = discord.Embed(title=f"User Info - {member.name}", color=discord.Color.blue())

    # ✅ Check if the user has an avatar before setting it
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)

    await ctx.send(embed=embed)

   
@bot.command()
async def remind(ctx, time: int, *, message: str):
    """Sets a reminder"""
    await ctx.send(f"⏳ Reminder set! I will remind you in {time} seconds.")
    await asyncio.sleep(time)
    await ctx.send(f"⏰ **Reminder:** {message}")

# Run the bot
bot.run(TOKEN)
