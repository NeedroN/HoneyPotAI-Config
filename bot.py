"""
Discord bot that answers with GPT when you mention it or DM it.
Keeps a short memory per channel so follow-up questions make sense.
"""

import os
from collections import defaultdict, deque

import discord
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# How many past messages per channel the bot remembers.
HISTORY_SIZE = 12

SYSTEM_PROMPT = (
    "You are a friendly helper in a Discord server. "
    "Keep answers short, use Discord markdown, and never ping @everyone."
)


# OPENAI_BASE_URL is picked up automatically, so a proxy or Azure endpoint works too.
ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# channel id -> last few messages
history = defaultdict(lambda: deque(maxlen=HISTORY_SIZE))


def ask_gpt(channel_id, author, text):
    """
    Send the channel's recent chat plus the new message, return the reply.
    """

    history[channel_id].append({"role": "user", "content": f"{author}: {text}"})

    response = ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history[channel_id]],
        max_tokens=500,
    )

    answer = response.choices[0].message.content.strip()
    history[channel_id].append({"role": "assistant", "content": answer})

    return answer


@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({len(client.guilds)} servers)")


@client.event
async def on_message(message):

    # Never answer ourselves or other bots.
    if message.author.bot:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    mentioned = client.user in message.mentions

    if not (is_dm or mentioned):
        return

    text = message.content.replace(f"<@{client.user.id}>", "").strip()

    if not text:
        await message.reply("Hey! Ask me something 👋")
        return

    if text.lower() == "!reset":
        history[message.channel.id].clear()
        await message.reply("Memory cleared for this channel.")
        return

    async with message.channel.typing():
        try:
            answer = ask_gpt(message.channel.id, message.author.display_name, text)
        except Exception as error:
            print("OpenAI error:", error)
            answer = "Something went wrong talking to the AI, try again in a bit."

    # Discord caps messages at 2000 characters.
    for start in range(0, len(answer), 1900):
        await message.reply(answer[start:start + 1900], mention_author=False)


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
