import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from common.config import BOT_TOKEN_CHECKER, CHANNEL_ID

bot = Bot(token=BOT_TOKEN_CHECKER)
dp = Dispatcher()

user_files = {}

def subscribe_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="عضویت در کانال", url="https://t.me/YourChannelLink")],
            [InlineKeyboardButton(text="بررسی عضویت", callback_data="check_subscribe")]
        ]
    )

@dp.message(CommandStart())
async def start_command(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        file_id = args[1]
        user_files[message.from_user.id] = file_id

        try:
            member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
            if member.status not in ("member", "administrator", "creator"):
                await message.answer("ابتدا عضو کانال شوید.", reply_markup=subscribe_keyboard())
                return
        except TelegramBadRequest:
            await message.answer("ابتدا عضو کانال شوید.", reply_markup=subscribe_keyboard())
            return

        await send_file(message, file_id)
    else:
        await message.answer("لینک معتبر نیست.")

@dp.callback_query(F.data == "check_subscribe")
async def check_sub(callback_query: types.CallbackQuery):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, callback_query.from_user.id)
        if member.status in ("member", "administrator", "creator"):
            file_id = user_files.get(callback_query.from_user.id)
            if file_id:
                await send_file(callback_query.message, file_id)
            else:
                await callback_query.message.answer("لینک معتبر نیست.")
        else:
            await callback_query.message.answer("عضویت تایید نشد.")
    except TelegramBadRequest:
        await callback_query.message.answer("عضویت تایید نشد.")

async def send_file(message: types.Message, file_id: str):
    try:
        sent = await message.answer_photo(file_id)
    except:
        try:
            sent = await message.answer_video(file_id)
        except:
            await message.answer("فایل معتبر نیست.")
            return

    await asyncio.sleep(15)
    try:
        await bot.delete_message(message.chat.id, sent.message_id)
    except:
        pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
