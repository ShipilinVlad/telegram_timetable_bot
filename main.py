import telebot
import logging
from telebot import types



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

token = "5153856526:AAGF8RuxbSoY_utKK_LCRRwcsyGflpKM3xs"

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(text="Функции", callback_data='greeting')
    markup.add(button)
    bot.send_message(chat_id=message.chat.id,
                     text="Привет, я помогу тебе не забыть о своём домашнем задании и помогу следить за "
                          "расписанием уроков и звонков! Если хочешь узнать больше о моих возможностях, "
                          "нажми кнопку ниже", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def functions(call):
    if call.data == 'greeting':
        bot.send_message(chat_id=call.from_user.id, text='Тут должен быть текст /help')
        bot.answer_callback_query(callback_query_id=call.id)


def main():
    bot.polling(non_stop=True)


if __name__ == '__main__':
    main()
