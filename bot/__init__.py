import asyncio
import random
import ujson
from pathlib import Path

import discord
from discord.ext import commands

import bot.database
from bot.database.models import Guild, Raid
from bot.utils import config, get_guild_prefix

__version__ = "0.1.0"

invite_link = "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&permissions=8192"

presence_strings = [
    "hosting raids",
    "@Ditto help",
    "@Ditto host",
    "catching shinies",
]


async def get_prefix(_bot, message):
    prefix = config.prefix
    if not isinstance(message.channel, discord.DMChannel):
        prefix = get_guild_prefix(_bot, message.guild.id)
    return commands.when_mentioned_or(prefix)(_bot, message)


bot = commands.AutoShardedBot(command_prefix=get_prefix)
bot.version = __version__
bot.active_commands = 0
bot.total_commands = 0
bot.remove_command("help")


async def preload_guild_data():
    guilds = await Guild.query.gino.all()
    d = dict()
    for guild in guilds:
        d[guild.id] = guild
    return d


async def preload_raid_data():
    raids = await Raid.query.gino.all()
    d = dict()
    for raid in raids:
        d[raid.id] = raid
    return d


@bot.event
async def on_ready():
    bot.invite = invite_link.format(bot.user.id)
    await database.setup()
    print(
        f"""Logged in as {bot.user}..
        Serving {len(bot.users)} users in {len(bot.guilds)} guilds
        Invite: {invite_link.format(bot.user.id)}
    """
    )
    with open("bot/pokemon/data/pokemon.json", "r") as f:
        bot.pokemon_images = ujson.load(f)
    bot.guild_data = await preload_guild_data()
    bot.raid_data = await preload_raid_data()
    bot.queue_data = dict()
    for raid in bot.raid_data.values():
        bot.queue_data[f"{raid.id}+{raid.host_id}"] = {
            "raid_id": raid.id,
            "user_id": raid.host_id,
            "guild_id": raid.guild_id,
        }
    bot.loop.create_task(presence_task())
    bot.loop.create_task(sync_guild_data())


async def presence_task():
    while True:
        await bot.change_presence(
            activity=discord.Game(random.choice(presence_strings))
        )
        await asyncio.sleep(60)


async def sync_guild_data():
    while True:
        try:
            guild_data = await preload_guild_data()
            if guild_data:
                bot.guild_data = guild_data
            raid_data = await preload_raid_data()
            if raid_data:
                bot.raid_data = raid_data
        except:
            pass
        await asyncio.sleep(300)


@bot.before_invoke
async def before_invoke(ctx):
    ctx.bot.total_commands += 1
    ctx.bot.active_commands += 1


@bot.after_invoke
async def after_invoke(ctx):
    ctx.bot.active_commands -= 1


def extensions():
    files = Path("bot", "cogs").rglob("*.py")
    for file in files:
        yield file.as_posix()[:-3].replace("/", ".")


def load_extensions(_bot):
    for ext in extensions():
        try:
            _bot.load_extension(ext)
        except Exception as ex:
            print(f"Failed to load extension {ext} - exception: {ex}")


def run():
    load_extensions(bot)
    bot.run(config.token)
