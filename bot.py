from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN, SUPPORT_RU_GROUP, SUPPORT_KZ_GROUP
from db import Database

import logging

# bot init
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)
db = Database('database.db')

# Start command
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
	if not db.user_exists(message.from_user.id):
		lang_menu = types.InlineKeyboardMarkup(row_width=2)
		lang_menu.add(types.InlineKeyboardButton(text='Русский', callback_data='lang_ru'), types.InlineKeyboardButton(text='Қазақша', callback_data='lang_kz'))
		
		await message.answer(f'<b>Пожалуйста, выберите язык:</b>\n', reply_markup=lang_menu)
	else:
		start_dialog = types.InlineKeyboardMarkup(row_width=1)
		start_dialog.insert(types.InlineKeyboardButton(text='Начать диалог', callback_data='start_dialog'))

		main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
		main_menu.insert(types.KeyboardButton('Настройки'))

		await bot.send_message(message.from_user.id, f'Привет, <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!)\n\n', reply_markup=start_dialog)
		await bot.send_message(message.from_user.id, f'Что желаешь?\n\n', reply_markup=main_menu)


# answer command
@dp.message_handler(commands=['answer'])
async def answer_cmd(message: types.Message):
	msg = message.text.split(' ')
	user_id = message.text.split(' ')[1]
	text = message.text.split(' ')[2]

	if len(msg) >= 4:
		msg.pop(0)
		msg.pop(0)
		
		msg_text = ' '.join(map(str, msg))
		
		try:
			await bot.send_message(user_id, msg_text)
		except:
			pass

	elif len(msg) == 3:
		try:
			await bot.send_message(user_id, text)
		except:
			pass


# stop command
@dp.message_handler(commands=['stop'])
async def stop_cmd(message: types.Message):
	await message.answer('Диалог остановлен!')
	# Заносит в бд что пользователь отключён от диалога
	# И сделать проверку в месс хэндлере, на то, что он подключен
	# А также в кнопке запуска дилога менять значение статуса в бд, на "online"

# callbacks handler
@dp.callback_query_handler(text_contains=['lang_'])
async def set_language(call: types.CallbackQuery):
	await bot.delete_message(call.from_user.id, call.message.message_id)
	
	if not db.user_exists(call.from_user.id):
		lang = call.data[5:]
		db.add_user(call.from_user.id, lang)

		start_dialog = types.InlineKeyboardMarkup(row_width=1)
		start_dialog.insert(types.InlineKeyboardButton(text='Начать диалог', callback_data='start_dialog'))
		await bot.send_message(call.from_user.id, f'Привет, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>!)\n\n', reply_markup=start_dialog)

# callbacks handler
@dp.callback_query_handler(text=['start_dialog'])
async def start_dialog(call: types.CallbackQuery):
	await call.message.edit_text('Диалог начался, пиши прямо внизу 👇')

# all messages handler
@dp.message_handler()
async def message_handler(message: types.Message):
	if message.chat.id != SUPPORT_RU_GROUP and message.chat.id != SUPPORT_KZ_GROUP:
		if db.get_lang(message.chat.id) == 'ru':
			await bot.send_message(SUPPORT_RU_GROUP, f'Пользователь <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> пишет:\n{message.text}\n\nЧтобы ответить введите: <code>/answer {message.from_user.id} ответ</code>')
		
		elif db.get_lang(message.chat.id) == 'kz':
			await bot.send_message(SUPPORT_KZ_GROUP, f'Пользователь <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> пишет:\n{message.text}\n\nЧтобы ответить введите: <code>/answer {message.from_user.id} ответ</code>')






if __name__ == '__main__':
	# bot polling
	executor.start_polling(dp, skip_updates=True)