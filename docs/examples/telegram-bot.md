# Example: Telegram Bot

A Telegram bot that verifies Boosty subscriptions and grants access to a private channel.

## Dependencies

```bash
pip install boostylib aiogram
```

## Code

```python
import asyncio
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from boostylib import BoostyClient
from boostylib.auth import EnvTokenStorage

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
BOOSTY_BLOG = os.environ["BOOSTY_BLOG"]
PRIVATE_CHANNEL_ID = int(os.environ["PRIVATE_CHANNEL_ID"])

bot = Bot(token=TELEGRAM_TOKEN)
router = Router()
boosty = BoostyClient(token_storage=EnvTokenStorage())


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Welcome! Use /verify <your_boosty_username> to check your subscription."
    )


@router.message(Command("verify"))
async def cmd_verify(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /verify <boosty_user_id>")
        return

    user_id = args[1].strip()
    status = await boosty.subscriptions.verify_subscription(BOOSTY_BLOG, user_id)

    if status.is_subscribed and status.is_paid:
        invite = await bot.create_chat_invite_link(
            PRIVATE_CHANNEL_ID, member_limit=1
        )
        await message.answer(
            f"Subscription confirmed: {status.level.name}\n"
            f"Here's your invite: {invite.invite_link}"
        )
    elif status.is_subscribed:
        await message.answer(
            "You have a free subscription. Upgrade to a paid tier for access."
        )
    else:
        await message.answer(
            f"No subscription found. Subscribe at boosty.to/{BOOSTY_BLOG}"
        )


async def main():
    async with boosty:
        dp = Dispatcher()
        dp.include_router(router)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables

```bash
export TELEGRAM_TOKEN=123456:ABC-DEF
export BOOSTY_BLOG=my_blog_username
export PRIVATE_CHANNEL_ID=-1001234567890
export BOOSTY_ACCESS_TOKEN=...
export BOOSTY_REFRESH_TOKEN=...
export BOOSTY_DEVICE_ID=...
```
