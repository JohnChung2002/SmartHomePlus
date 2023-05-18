from discord_webhook import DiscordWebhook, DiscordEmbed

webhook = DiscordWebhook(
    url="https://discord.com/api/webhooks/1108083260917035058/oArD4QC5HjImzXkxPmoFUybyhv2OMFYuD9YDkgWO4XcAEYznUuNgF4YSz9YM8Ir912nP", 
    username="Home Automation Bot"
)

embed = DiscordEmbed(
    title="Testing Discord Webhook", 
    description="Mak Kau Hijau", 
    color="03b2f8",
    url = "https://dashboard.digitalserver.tech/"
)

webhook.add_embed(embed)
response = webhook.execute()