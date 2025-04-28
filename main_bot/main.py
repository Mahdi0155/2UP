import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from common.config import BOT_TOKEN_MAIN, OWNER_ID, CHECKER_BOT_USERNAME

bot = Bot(token=BOT_TOKEN_MAIN)
dp = Dispatcher()

class UploadStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_caption = State()
    waiting_for_timelink = State()

force_join_enabled = False

def admin_panel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="آپلود فایل جدید", callback_data="upload_file")],
            [InlineKeyboardButton(text="عضویت اجباری", callback_data="force_join")],
            [InlineKeyboardButton(text="ارسال پیام همه‌گانی", callback_data="broadcast")],
        ]
    )

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("ربات آماده سرویس‌دهی است.")

@dp.message(Command("panel"))
async def panel(message: types.Message):
    if message.from_user.id == OWNER_ID:
        await message.answer("پنل مدیریت:", reply_markup=admin_panel_keyboard())

@dp.callback_query(F.data == "upload_file")
async def upload_file_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("لطفاً فایل را ارسال کنید (عکس یا ویدیو)...")
    await state.set_state(UploadStates.waiting_for_file)

@dp.message(UploadStates.waiting_for_file)
async def file_received(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    await state.update_data(file_id=file_id)
    await message.answer("لطفاً کپشن فایل را ارسال کنید...")
    await state.set_state(UploadStates.waiting_for_caption)

@dp.message(UploadStates.waiting_for_caption)
async def caption_received(message: types.Message, state: FSMContext):
    await state.update_data(caption=message.text)
    await message.answer("لطفاً تایم نیل فایل را وارد کنید یا بنویسید 'ندارد'...")
    await state.set_state(UploadStates.waiting_for_timelink)

@dp.message(UploadStates.waiting_for_timelink)
async def timelink_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_id = data["file_id"]
    caption = data["caption"]
    timelink = message.text

    preview_text = f"کپشن: {caption}\nتایم نیل: {timelink}"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="مشاهده فایل", url=f"https://t.me/{CHECKER_BOT_USERNAME}?start={file_id}")]
        ]
    )
    sent = await message.answer(preview_text, reply_markup=keyboard)

    await asyncio.sleep(15)
    try:
        await bot.delete_message(sent.chat.id, sent.message_id)
    except:
        pass
    await state.clear()

@dp.callback_query(F.data == "force_join")
async def toggle_force_join(callback: types.CallbackQuery):
    global force_join_enabled
    force_join_enabled = not force_join_enabled
    status = "فعال" if force_join_enabled else "غیرفعال"
    await callback.message.answer(f"عضویت اجباری: {status}")

@dp.callback_query(F.data == "broadcast")
async def broadcast_coming_soon(callback: types.CallbackQuery):
    await callback.message.answer("این ویژگی بعداً اضافه خواهد شد.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
