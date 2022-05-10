import telebot
import logging
from telebot import types
import database
import re


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

token = "5153856526:AAH7uuXBS4N9Yg8t0rEyU3Dv1ciMfsOmD6E"
bot = telebot.TeleBot(token)

db = database.DataBase('data/timetable_database')

params = {'adding_timetable': False, 'current_timetable': [], 'current_user': '', 'current_day': []}
week_days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']


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
               '/delete_timetable - спрашивает, какое удалить расписание с помощью кнопок\n\n'
               '/edit_timetable - спрашивает, какое отредактировать расписание с помощью кнопок\n\n'
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
           '/delete_timetable - спрашивает, какое удалить расписание с помощью кнопок\n\n'
           '/edit_timetable - спрашивает, какое отредактировать расписание с помощью кнопок\n\n'
           'Сообщение типа "Название предмета": "задание" - добавляет задание в базу данных, '
           'если такой предмет уже есть, уведомляет об этом и спрашивает, удалить старое или нет.')
    bot.send_message(chat_id=message.from_user.id, text=out)


@bot.message_handler(commands=['set_timetable'])
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
    bot.send_message(chat_id=message.from_user.id,
                     text=f"Введите расписание на {week_days[len(params['current_timetable'])].capitalize()}")
    bot.send_message(chat_id=message.from_user.id, text=f"Введите урок №{len(params['current_day']) + 1}")


@bot.message_handler(commands=['cancel'])
def cancel(message):
    params['adding_timetable'] = False
    params['current_day'] = []
    params['current_timetable'] = []
    params['current_user'] = ''
    bot.send_message(chat_id=message.from_user.id, text="Действие отменено",
                     reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['save'])
def save(message):
    db.query(f"""DELETE 
                 FROM lessons 
                 WHERE id={params['current_user']}""")
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

    all_users = [elem[0] for elem in db.select_with_fetchall("SELECT user_id "
                                                             "FROM users")]

    bot.send_message(chat_id=message.from_user.id, text='Сохраняю, подождите 🕑')
    lessons_ids = []

    for i in range(len(params['current_timetable'])):
        elem = params['current_timetable'][i]
        day = week_days[i]
        data = elem[day]
        for j in range(len(data)):
            lesson_info = [a.strip(' ') for a in data[j].split(', ')]
            lesson_name = lesson_info[0]
            lesson_start = lesson_info[1]
            lesson_end = lesson_info[2]
            user = params['current_user']

            if not db.query(f"""SELECT id 
                                FROM lessons 
                                WHERE lesson_name='{lesson_name}' AND start_time='{lesson_start}' 
                                AND end_time='{lesson_end}' AND user={user} AND day='{day}'"""):
                db.query(f"""INSERT INTO lessons(lesson_name, start_time, end_time, user, day) 
                             VALUES('{lesson_name}', '{lesson_start}', '{lesson_end}', {user}, '{day}')""")

            lesson_id = db.select_with_fetchone(f"""SELECT id 
                                                    FROM lessons 
                                                    WHERE lesson_name='{lesson_name}' AND start_time='{lesson_start}' 
                                                    AND end_time='{lesson_end}' AND user={user} AND day='{day}'""")[0]

            lessons_ids.append(lesson_id)

    if params['current_user'] in all_users:
        db.query(f"""UPDATE users 
                     SET lessons_ids = '{' '.join([str(elem) for elem in lessons_ids])}'""")
    else:
        db.query(f"""INSERT INTO users(user_id, lessons_ids) 
                     VALUES({params['current_user']}, '{' '.join([str(elem) for elem in lessons_ids])}')""")

    bot.send_message(chat_id=message.from_user.id, text="Расписание сохранено 👍",
                     reply_markup=types.ReplyKeyboardRemove())

    params['current_timetable'] = []
    params['current_day'] = []
    params['current_user'] = ''
    params['adding_timetable'] = False


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
    bot.send_message(chat_id=message.from_user.id,
                     text=f"Введите расписание на {week_days[len(params['current_timetable'])].capitalize()}")
    bot.send_message(chat_id=message.from_user.id, text=f"Введите урок №{len(params['current_day']) + 1}")


@bot.message_handler(commands=['homework'])
def homework(message):
    text = message.text.split(maxsplit=1)
    subject = text[1] if len(text) > 1 else ''
    out = 'Вот домашнее задание '
    if subject:
        result = db.select_with_fetchall(f"""SELECT subject, text 
                                             FROM homework 
                                             WHERE subject='{subject}' AND user_id={message.from_user.id}""")
        out += f'по предмету {subject}:\n'
    else:
        result = db.select_with_fetchall(f"""SELECT subject, text 
                                             FROM homework 
                                             WHERE user_id={message.from_user.id}""")
        out += f'по всем предметам:\n'
    if not result:
        out = 'Ничего не найдено'
    else:
        out += '\n'.join([f"{i + 1}) {result[i][0]}: {result[i][1]}" for i in range(len(result))])
    bot.send_message(chat_id=message.from_user.id, text=out)


@bot.message_handler(commands=['delete_task'])
def delete_task(message):
    text = message.text.split(maxsplit=1)
    if len(text) == 1:
        bot.send_message(chat_id=message.from_user.id,
                         text='Для удаления задания введите /delete_task <название предмета>')
    else:
        try:
            subject = text[1]
            old_homework = str(db.select_with_fetchone(f"""SELECT homework_ids 
                                                           FROM users 
                                                           WHERE user_id={message.from_user.id}""")[0]).split()
            to_delete = db.select_with_fetchone(f"""SELECT id 
                                                    FROM homework
                                                    WHERE user_id={message.from_user.id} AND subject='{subject}'""")[0]
            old_homework.remove(str(to_delete))
            db.query(f"""UPDATE users 
                         SET homework_ids='{' '.join(old_homework)}' 
                         WHERE user_id={message.from_user.id}""")
            db.query(f"""DELETE 
                         FROM homework 
                         WHERE subject='{subject}'""")
            bot.send_message(chat_id=message.from_user.id, text=f"Задание по предмету {subject} удалено")
        except TypeError:
            bot.send_message(chat_id=message.from_user.id, text="По этому предмету нет заданий")


@bot.message_handler(commands=['timetable'])
def timetable(message):
    table = db.select_with_fetchall(f"""SELECT lesson_name, start_time, end_time, day 
                                        FROM lessons 
                                        WHERE user={message.from_user.id}""")
    if table:
        out = dict()
        out_text = ''
        for elem in table:
            if elem[3] not in out.keys():
                out[elem[3]] = [f'{elem[0]}, {elem[1]}, {elem[2]}']
            else:
                out[elem[3]].append(f'{elem[0]}, {elem[1]}, {elem[2]}')
        for key in out.keys():
            out_text += f"{str(key).capitalize()}:\n"
            for i in range(len(out[key])):
                out_text += f"{i + 1}) {out[key][i]}\n"
            out_text += '\n'
        bot.send_message(chat_id=message.from_user.id, text=out_text)
    else:
        bot.send_message(chat_id=message.from_user.id, text="Нет сохранённого расписания")


@bot.message_handler(content_types=['text'])
def getting_tasks(message):
    if params['adding_timetable']:
        line = message.text
        str_type = r".*,\s.*,\s.*"
        res = re.fullmatch(str_type, line)
        if res is not None and line.count(',') == 2:
            params['current_day'].append(line)
            bot.send_message(chat_id=message.from_user.id, text=f"Введите урок №{len(params['current_day']) + 1} "
                                                                f"или нажмите одну из кнопок ниже")
        else:
            bot.send_message(chat_id=message.from_user.id, text="Неверный формат ввода, повторите попытку")
    else:
        line = message.text
        str_type = r".*:.*"
        res = re.fullmatch(str_type, line)
        if res is not None and line.count(":") == 1:
            if not db.select_with_fetchone(f"""SELECT id 
                                               FROM users 
                                               WHERE user_id={message.from_user.id}"""):
                db.query(f"""INSERT INTO users(user_id) 
                             VALUES({message.from_user.id})""")
            subject = line[:line.find(':')]
            text = line[line.find(':') + 1:]
            user = message.from_user.id
            previous = db.select_with_fetchone(f"""SELECT text 
                                                   FROM homework 
                                                   WHERE subject='{subject}' AND user_id={user}""")
            if previous:
                bot.send_message(chat_id=message.from_user.id,
                                 text=f"Старое задание по предмету {subject}: {previous[0]}")
                bot.send_message(chat_id=message.from_user.id,
                                 text=f"Новое задание по предмету {subject}: {text}")
                db.query(f"""UPDATE homework 
                             SET text='{text}' 
                             WHERE user_id={user} AND subject='{subject}'""")
            else:
                db.query(f"""INSERT INTO homework(subject, text, user_id) 
                             VALUES('{subject}', '{text}', {user})""")
                homework_id = db.select_with_fetchone(f"""SELECT id 
                                                          FROM homework 
                                                          WHERE subject='{subject}' AND text='{text}' 
                                                          AND user_id={user}""")[0]
                new_ids = [elem[0] for elem in db.select_with_fetchall(f"""SELECT homework_ids 
                                                                           FROM users 
                                                                           WHERE user_id={message.from_user.id}""")]
                if new_ids[0]:
                    new_ids.append(homework_id)
                else:
                    new_ids = [homework_id]
                db.query(f"""UPDATE users 
                             SET homework_ids='{' '.join([str(elem) for elem in new_ids])}' 
                             WHERE user_id={message.from_user.id}""")
            bot.send_message(chat_id=message.from_user.id, text=f"Домашнее задание по предмету {subject} сохранено")
        else:
            bot.send_message(chat_id=message.from_user.id, text="Извините, я не понял ☹️ Может /help?")


def main():
    bot.polling(non_stop=True)


if __name__ == '__main__':
    main()
