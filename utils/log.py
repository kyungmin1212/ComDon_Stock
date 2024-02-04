import dhooks
from settings import env_settings


async def price_send_message(message):
    async with dhooks.Webhook.Async(env_settings.DISCORD_PRICE_WEBHOOK_URL) as hook:
        await hook.send(message)


async def buy_sell_message(message):
    async with dhooks.Webhook.Async(env_settings.DISCORD_BUY_SELL_WEBHOOK_URL) as hook:
        await hook.send(message)
