import telebot
import logging
from telebot import types
import database
import re


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

token = "5153856526:AAFHm8vI377a8wj1l9Xy2DoPT-QBJ0FuUrc"
bot = telebot.TeleBot(token)

db = database.DataBase('data/timetable_database')


params = {'adding_timetable': False, 'current_timetable': [], 'current_user': '', 'current_day': []}
week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(text="Функции", callback_data='greeting')
    markup.add(button)
    bot.send_message(chat_id=message.from_user.id,
                     text="Привет, я помогу тебе не забыть о своём домашнем задании и помогу следить за "
                          "расписанием уроков и звонков! Если хочешь узнать больше о моих возможностях, "
                          "нажми кнопку ниже", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def functions(call):
    if call.data == 'greeting':
        out = ('/start - здоровается и выдаёт информацию о функционале\n\n'
               '/help - список команд с разъяснением\n\n'
               '/add_timetable - просит ввести расписание в формате "Предмет" "время начала" "время окончания"\n\n'
               '/lesson - показывает время окончания и название текущего урока, '
               'время начала и название следующего(либо пишет, что нет информации)\n\n'
               '/homework - выдаёт всю невыполненную домашнюю работу\n\n'
               '/delete_task "название предмета" - удаляет из бд задание по ключу или говорит, что задания нет.\n\n'
               '/timetable - выдаёт всё расписание на неделю с временем начала и окончания урока \n\n'
               '/delete_timetable - спрашивает, какое удалить расписание с помошью кнопок\n\n'
               '/edit_timetable - спрашивает, какое отредактировать расписание с помошью кнопок\n\n'
               'Сообщение типа "Название предмета": "задание" - добавляет задание в базу данных, '
               'если такой предмет уже есть, уведомляет об этом и спрашивает, удалить старое или нет.')
        bot.send_message(chat_id=call.from_user.id, text=out)
        bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(commands=['help'])
def help_message(message):
    out = ('/start - здоровается и выдаёт информацию о функционале\n\n'
           '/help - список команд с разъяснением\n\n'
           '/add_timetable - просит ввести расписание в формате "Предмет" "время начала" "время окончания"\n\n'
           '/lesson - показывает время окончания и название текущего урока, '
           'время начала и название следующего(либо пишет, что нет информации)\n\n'
           '/homework - выдаёт всю невыполненную домашнюю работу\n\n'
           '/delete_task "название предмета" - удаляет из бд задание по ключу или говорит, что задания нет.\n\n'
           '/timetable - выдаёт всё расписание на неделю с временем начала и окончания урока \n\n'
           '/delete_timetable - спрашивает, какое удалить расписание с помошью кнопок\n\n'
           '/edit_timetable - спрашивает, какое отредактировать расписание с помошью кнопок\n\n'
           'Сообщение типа "Название предмета": "задание" - добавляет задание в базу данных, '
           'если такой предмет уже есть, уведомляет об этом и спрашивает, удалить старое или нет.')
    bot.send_message(chat_id=message.from_user.id, text=out)


@bot.message_handler(commands=['add_timetable'])
def add_timetable(message):
    params['adding_timetable'] = True
    params['current_day'] = []
    params['current_timetable'] = []
    params['current_user'] = message.from_user.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    markup.row('/cancel', '/save', '/next')
    bot.send_message(message.from_user.id, text='Формат ввода: "название", "начало", "конец"\n'
                                                'Нажмите "cancel" для отмены ввода, '
                                                '"save" для сохранения расписания, '
                                                '"next" для перехода к следующему дню', reply_markup=markup)
    bot.send_message(chat_id=message.from_user.id, text=f"Введите урок №{len(params['current_day']) + 1}")


@bot.message_handler(commands=['cancel'])
def cancel(message):
    params['adding_timetable'] = False
    params['current_day'] = []
    params['current_timetable'] = []
    params['current_user'] = ''
    bot.send_message(chat_id=message.from_user.id, text=f"Действие отменено",
                     reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['save'])
def cancel(message):
    day = dict()
    day[week_days[len(params['current_timetable'])]] = params['current_day']
    params['current_timetable'].append(day)
    params['current_day'] = []

    # db.select_with_fetchall("SELECT user_id FROM users")

    bot.send_message(chat_id=message.from_user.id, text='Сохраняю, подождите 🕑')
    print(params)

    # for i in range(len(params['current_timetable'])):
    #     elem = params['current_timetable'][i]
    #     key = elem.keys()[0]
    #     data = elem[key]
    #     for j in range(len(data)):
    #         db.query(f"""INSERT INTO lessons (lesson_name, start_time, end_time, user) VALUES ({}, {}, {}, {})""")

    # db.query(f"""INSERT INTO lessons (lesson_name, start_time, end_time, user) VALUES ({}, {}, {}, {})""")

    # if params['current_user'] in db.select_with_fetchall("""SELECT user_id FROM users""")[0]:
    #     pass
    # else:
    #     db.query(f"""INSERT INTO users (user_id, lessons_ids) VALUES ({params['current_user']}, {})""")

    #
    bot.send_message(chat_id=message.from_user.id, text="Расписание сохранено 👍")
    #
    # adding_timetable[0] = False
    # current_timetable[0] = []
    # current_user[0] = ''
    params['adding_timetable'] = False
    pass


@bot.message_handler(commands=['next'])
def next_day(message):
    day = dict()
    day[week_days[len(params['current_timetable'])]] = params['current_day']
    params['current_timetable'].append(day)
    params['current_day'] = []
    elem_num = len(params['current_timetable']) - 1
    out = '\n'.join([f"{i + 1}) {params['current_timetable'][elem_num][week_days[elem_num]][i]}"
                     for i in range(len(params['current_timetable'][len(params['current_timetable']) - 1]
                                        [week_days[len(params['current_timetable']) - 1]]))])
    bot.send_message(chat_id=message.from_user.id,
                     text=f"Добавлено расписание на "
                          f"{week_days[len(params['current_timetable']) - 1].capitalize()}: \n{out}")


@bot.message_handler(commands=['lesson'])
def lesson(message):
    pass


@bot.message_handler(commands=['homework'])
def homework(message):
    pass


@bot.message_handler(commands=['delete_task'])
def delete_task(message):
    pass


@bot.message_handler(commands=['timetable'])
def timetable(message):
    pass


@bot.message_handler(commands=['delete_timetable'])
def delete_timetable(message):
    pass


@bot.message_handler(commands=['edit_timetable'])
def edit_timetable(message):
    pass


@bot.message_handler(content_types=['text'])
def getting_tasks(message):
    if params['adding_timetable']:
        line = message.text
        str_type = r".*,\s.*,\s.*"
        res = re.fullmatch(str_type, line)
        if res is not None and line.count(',') == 2:
            print(line)
            params['current_day'].append(line)
            bot.send_message(chat_id=message.from_user.id, text=f"Введите урок №{len(params['current_day']) + 1} "
                                                                f"или нажмите одну из кнопок ниже")
        else:
            bot.send_message(chat_id=message.from_user.id, text="Неверный формат ввода, повторите попытку")
    else:
        pass
    print(params['current_user'])
    print(params['adding_timetable'])
    print(params['current_day'])
    print(params['current_timetable'])


def main():
    bot.polling(non_stop=True)


if __name__ == '__main__':
    main()
