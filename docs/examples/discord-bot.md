# Example: Discord Bot

A Discord bot that assigns roles based on Boosty subscription levels.

## Dependencies

```bash
pip install boostylib discord.py
```

## Code

```python
import os

import discord
from discord.ext import commands

from boostylib import BoostyClient
from boostylib.auth import EnvTokenStorage

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
BOOSTY_BLOG = os.environ["BOOSTY_BLOG"]

# Map Boosty level names → Discord role names
LEVEL_ROLE_MAP = {
    "Basic": "Boosty Basic",
    "Premium": "Boosty Premium",
    "VIP": "Boosty VIP",
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
boosty = BoostyClient(token_storage=EnvTokenStorage())


@bot.command()
async def verify(ctx, boosty_user_id: str):
    """Verify Boosty subscription and assign role."""
    status = await boosty.subscriptions.verify_subscription(
        BOOSTY_BLOG, boosty_user_id
    )

    if not status.is_subscribed:
        await ctx.send("No active subscription found.")
        return

    role_name = LEVEL_ROLE_MAP.get(status.level.name)
    if not role_name:
        await ctx.send(f"Subscribed ({status.level.name}), but no role mapping configured.")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"Role '{role_name}' not found on this server.")
        return

    await ctx.author.add_roles(role)
    await ctx.send(f"Verified! Assigned role: **{role_name}**")


@bot.event
async def on_ready():
    await boosty.__aenter__()
    print(f"Bot ready: {bot.user}")


bot.run(DISCORD_TOKEN)
```

## Environment Variables

```bash
export DISCORD_TOKEN=...
export BOOSTY_BLOG=my_blog_username
export BOOSTY_ACCESS_TOKEN=...
export BOOSTY_REFRESH_TOKEN=...
export BOOSTY_DEVICE_ID=...
```
