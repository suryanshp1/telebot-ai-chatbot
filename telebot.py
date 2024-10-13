import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import openai

logging.basicConfig(level=logging.INFO)

load_dotenv()

GROQ_API_TOKEN = os.getenv('GROQ_API_KEY')
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher()

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_TOKEN
)

class Reference:
    """
    A class to store previous message response from GROQ API
    """
    def __init__(self) -> None:
        self.response = ""

reference = Reference()

def clear_past() -> None:
    """
    A function to clear previous conversation and context
    """
    reference.response = ""


@dispatcher.message(CommandStart())
async def welcome(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.reply("Hi,\n I'm EchoBot!\n\nCreated by Suryansh Pandey. How can I help you?")

@dispatcher.message(Command("clear"))
async def clear(message: Message) -> None:
    """
    This handler to clear previous conversation and context
    """
    clear_past()
    await message.reply("I have cleared the past conversation and context")

@dispatcher.message(Command("help"))
async def helper(message: Message) -> None:
    """
    This handler to display the help menu
    """

    help_command = """
    Hi There, I'm a Telegram bot created by Suryansh. I can do the following things:
    - /start - Start conversation
    - /clear - Clear past conversation and context
    - /help - Show this Help menu

    I hope you enjoy my service. If you have any questions, feel free to ask. I'm always happy to help. Have a great day! :)
    """
    await message.reply(help_command)

@dispatcher.message()
async def ai_bot(message: Message) -> None:
    """
    This handler process the user's input and return the response from GROQ API
    """
    logging.info(f">>> USER: \n\t{message.text}")
    response = client.chat.completions.create(
        messages=[
            {"role": "assistant", "content": reference.response},
            {"role": "user", "content": message.text}
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=1024
    )

    reference.response = response.choices[0].message.content

    logging.info(f">>> Assistant: \n\t{response.choices[0].message.content}")
    await bot.send_message(chat_id=message.chat.id, text=reference.response)

async def main() -> None:
    await dispatcher.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())