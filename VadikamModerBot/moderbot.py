import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from filters import IsAdminFilter

# log level
logging.basicConfig(level=logging.INFO)

# .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

# bot init
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# activate filters
dp.filters_factory.bind(IsAdminFilter)


# remove new user joined messages
@dp.message_handler(content_types=["new_chat_members", "left_chat_member"])
async def on_user_joined(message: types.Message):
    await message.delete()


# # remove left user joined messages
# @dp.message_handler(content_types=["left_chat_member"])
# async def on_user_left(message: types.Message):
#     await message.delete()


# ban command (admins only!)
@dp.message_handler(is_admin=True, commands=["ban"], commands_prefix="!/")
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply("This command must be answer on message")
        return

    await message.bot.delete_message(
        GROUP_ID, message.message_id,
    )
    await message.bot.kick_chat_member(
        chat_id=GROUP_ID, user_id=message.reply_to_message.from_user.id
    )

    await message.reply_to_message.reply("User banned!")


# # echo
# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer(message.text)


# checking for bad words
@dp.message_handler()
async def filter_messages(message: types.Message):
    if "bad word" in message.text:
        # profanity detected, remove
        await message.delete()


# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
