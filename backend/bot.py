import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Correctly load .env file
load_dotenv()

# Correct variable name
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Prevent bot from running if token is missing
if TOKEN is None:
    raise ValueError("ERROR: Discord bot token is missing! Check your .env file.")

# Correct intents setting
intents = discord.Intents.default()
intents.message_content = True 

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: When bot is ready
@bot.event
async def on_ready():
    print(f" DizBot is online as {bot.user}")

# Command: Say hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!v")

# Run the bot
bot.run(TOKEN)
