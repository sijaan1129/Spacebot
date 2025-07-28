import asyncio
from urllib.parse import quote_plus
import aiohttp
import dotenv
import os
import sqlite3
import time

from rich.traceback import install
from rich.console import Console
from rich.progress import track
from rich.theme import Theme

import asyncpraw
import topgg

from discord.ext import commands
import discord

from utilities.helpers.utils import get_prefix
from googletrans import Translator
translator = Translator()


install()
dotenv.load_dotenv()

custom_theme = Theme({"success": "green", "error": "bold red"})

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix=(get_prefix),
    description="""SpaceBot has many utility and fun commands that you can use! Also comes with music player!""",
    intents=intents,
    case_insensitive=True,
)
bot.console = Console(theme=custom_theme)
bot.topggpy = topgg.DBLClient(
    bot,
    os.getenv("TOPGG_TOKEN"),
    autopost=True,
    post_shard_count=True,
)
bot.reddit = asyncpraw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent="Spacebot",
)

bot.db = sqlite3.connect("database.db")
bot.dbcursor = bot.db.cursor()
bot.startTime = time.time()

async def session(bot):
    bot.httpsession = aiohttp.ClientSession()


asyncio.get_event_loop().run_until_complete(session(bot))


@bot.event
async def on_ready():
    print("Logged in as")
    bot.console.print(bot.user.name, style="success")
    bot.console.print(bot.user.id, style="success")
    
    print("------")
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(
            name=f"on {len(bot.guilds)} servers, {len(list(bot.get_all_members()))} members. | .help"
        ),
    )


@bot.message_command(name="Translate to English", guild_ids=[905904010760966164])
async def translate_to_en(ctx,message:discord.Message):
    result = translator.translate(message.content)
    await ctx.respond(embed=discord.Embed(title=f"Translation",description=result.text).set_footer(text=f"{result.src} to {result.dest}"))



@bot.message_command(name="Convert to QR code",guild_ids=[905904010760966164])
async def to_qr(ctx,message:discord.Message):
    try:
        await ctx.respond(embed=discord.Embed(title="QR code", description=f"Content: ```{message}```").set_image(f"https://api.dhravya.me/qrcode?query={quote_plus(message)}").set_footer(text="Powered by https://api.dhravya.me"))
    except Exception as e:
        await ctx.respond("An error occured: "+e)


files = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        files.append(f"cogs.{filename[:-3]}")
        pass

bot.load_extension("jishaku")
for file in track(files, description="Loading all cogs...."):
    bot.load_extension(file)


#* Running the bot
bot.run(os.getenv("BOT_TOKEN"))
