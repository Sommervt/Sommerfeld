enabled = True

async def run(bot, message):
    await message.channel.send(f"Hola, {message.author.name}! Este comando está en Python.")

