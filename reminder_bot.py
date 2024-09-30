import datetime
import shelve
import logging
import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telebot import TeleBot


def schedule_reminders(chat_id, reminder_times, training_day=None):
    try:
        # Удаляем предыдущие задания, если есть
        scheduler.remove_all_jobs()

        for day, reminder_time in reminder_times.items():
            day_number = get_day_number(day)
            if day_number is None:
                bot.send_message(chat_id,
                                 f"Неверный день недели: {day}. Пожалуйста, используйте полное название дня недели.")
                continue

            scheduler.add_job(
                send_reminder_with_program,
                trigger=CronTrigger(day_of_week=day_number, hour=int(reminder_time.split(':')[0]),
                                    minute=int(reminder_time.split(':')[1])),
                args=[chat_id, training_day]
            )
    except ValueError as e:
        bot.send_message(chat_id, f"Ошибка в формате времени: {str(e)}. Пожалуйста, введите время в формате ЧЧ:ММ.")
    except Exception as e:
        # Запись ошибки в лог
        logging.error(f"Ошибка при планировании напоминаний: {str(e)}")
        bot.send_message(chat_id, "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")

# Инициализация бота
bot: TeleBot = telebot.TeleBot('7508611106:AAFIcwYelkeOcgCwhhHzwNFtVTzPx5t4eGI')

# Планировщик для отправки напоминаний
scheduler = BackgroundScheduler()
scheduler.start()

# Хранилище для данных о пользователях
data_store = shelve.open('user_data.db')

# Программы тренировок
training_programs = {
    1: """Тренировка 1:
Бег: 15-20 минут
Спина: Подтягивания
    [3 подхода по 10-15 повторений]
Грудь: Жим штанги лёжа широким хватом 
    [3 подхода по 10-15 повторений]
Ноги: Жим ногами в тренажёре
    [3 подхода по 10-15 повторений]
Плечи: Отведение рук с гантелями в стороны
    [3 подхода по 10-15 повторений]
Бицепс: Подъём штанги стоя
    [3 подхода по 10-15 повторений]
Трицепс: Разгибание рук в тренажёре
    [3 подхода по 10-15 повторений]
Пресс: Сгибание ног в висе
    [3 подхода по 15-20 повторений]
Спина + ягодицы: Гиперэкстензия
    [3 подхода по 10-15 повторений]
Бег: 15-20 минут""",

    2: """Тренировка 2:
Бег: 15-20 минут
Спина: Тяга штанги в наклоне 
    [3 подхода по 10-15 повторений]
Грудь: Отжимания от пола 
    [3 подхода по 10-15 повторений]
Ноги: Выпады с гирями
    [3 подхода по 10-15 повторений]
Плечи: Жим гантелей над собой, локти в стороны
    [3 подхода по 10-15 повторений]
Бицепс: Сгибание рук с гантелями поочередно к противоположному плечу
    [3 подхода по 10-15 повторений]
Трицепс: Отжимания на брусьях, локти прижаты
    [3 подхода по 10-15 повторений]
Пресс: Лёжа но полу, "велосипед"
    [3 подхода по 15-20 повторений]
Спина + ягодицы: Гиперэкстензия
    [3 подхода по 10-15 повторений]
Бег: 15-20 минут""",

    3: """Тренировка 3:
Бег: 15-20 минут
Спина: Тяга троса сидя в тренажёре 
    [3 подхода по 10-15 повторений]
Грудь: Отжимания на брусьях локти в стороны 
    [3 подхода по 10-15 повторений]
Ноги: Приседания со штангой
    [3 подхода по 10-15 повторений]
Плечи: Подтягивания в наклоне широким хватом
    [3 подхода по 10-15 повторений]
Бицепс: Сгибание рук с гантелями сидя, ладонями наружу
    [3 подхода по 10-15 повторений]
Трицепс: Французский жим гантелей лёжа
    [3 подхода по 10-15 повторений]
Пресс: Скручивания лёжа на полу
    [3 подхода по 15-20 повторений]
Спина + ягодицы: Гиперэкстензия
    [3 подхода по 10-15 повторений]
Бег: 15-20 минут"""
}


# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    user_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    bot.send_message(message.chat.id,
                     f"Привет, {user_name} {user_last_name}! Я бот, который будет напоминать тебе о тренировках.")

    # Сохраняем пользователя
    if str(message.chat.id) not in data_store:
        data_store[str(message.chat.id)] = {
            'first_name': user_name,
            'last_name': user_last_name,
            'reminder_times': {},
            'training_history': []
        }

    # Предлагаем выбрать дни и время для тренировок
    bot.send_message(message.chat.id,
                     "Выбери дни недели и время для тренировок. Введи в формате: Понедельник 09:00, Среда 18:00 и т.д.")


# Команда для установки напоминаний
@bot.message_handler(commands=['set_reminders'])
def set_reminders(message):
    bot.send_message(message.chat.id,
                     "Выбери дни недели и время для тренировок. Введи в формате: Понедельник 09:00, Среда 18:00 и т.д.")


# Обработка введённых пользователем дней и времени напоминаний
@bot.message_handler(func=lambda message: any(day in message.text.lower() for day in
                                              ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота',
                                               'воскресенье']))
def handle_reminder_times(message):
    try:
        reminder_data = message.text.split(',')
        user_reminder_times = {}

        for data in reminder_data:
            day_time = data.strip().split(' ')
            day_of_week = day_time[0].capitalize()
            time_of_day = day_time[1]

            if validate_time_format(time_of_day):
                user_reminder_times[day_of_week] = time_of_day

        if user_reminder_times:
            user_data = data_store[str(message.chat.id)]
            user_data['reminder_times'] = user_reminder_times
            data_store[str(message.chat.id)] = user_data

            bot.send_message(message.chat.id,
                             f"Напоминания установлены на: {', '.join([f'{day} {time}' for day, time in user_reminder_times.items()])}")

            # Запуск напоминаний
            schedule_reminders(message.chat.id, user_reminder_times)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, введи корректное время в формате ЧЧ:ММ.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


# Проверка правильности формата времени
def validate_time_format(time_str):
    try:
        datetime.datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


# Планирование отправки напоминаний
def schedule_reminders(chat_id, reminder_times):
    try:
        # Удаляем предыдущие задания, если есть
        scheduler.remove_all_jobs()

        for day, reminder_time in reminder_times.items():
            day_number = get_day_number(day)

            # Программа тренировок по дню
            training_day = (day_number % 3) + 1

            scheduler.add_job(
                send_reminder_with_program,
                trigger=CronTrigger(day_of_week=day_number, hour=int(reminder_time.split(':')[0]),
                                    minute=int(reminder_time.split(':')[1])),
                args=[chat_id, training_day]
            )
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при планировании напоминаний: {str(e)}")

fact_list = [
    "Регулярные тренировки улучшают настроение и снижают уровень стресса.",
    "Физическая активность способствует здоровью сердечно-сосудистой системы.",
    "Занятия спортом могут увеличить продолжительность жизни.",
    "Силовые тренировки помогают поддерживать здоровый уровень костной массы.",
    "Физическая активность улучшает качество сна.",
    "Регулярные упражнения помогают поддерживать здоровый вес."
]


# Команда для отправки случайного факта
@bot.message_handler(commands=['fact'])
def fact_message(message):
    random_fact = random.choice(fact_list)
    bot.reply_to(message, f'Факт о тренировках: {random_fact}')

# Функция для отправки напоминания и программы тренировок
def send_reminder_with_program(chat_id, training_day):
    try:
        program = training_programs[training_day]
        bot.send_message(chat_id, f"Пора тренироваться! Вот твоя программа на сегодня:\n\n{program}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {str(e)}")


# Преобразование названия дня недели в номер
def get_day_number(day_name):
    days = {
        'Понедельник': 0,
        'Вторник': 1,
        'Среда': 2,
        'Четверг': 3,
        'Пятница': 4,
        'Суббота': 5,
        'Воскресенье': 6
    }
    day_name = day_name.capitalize()
    try:
        return days.get(day_name, None)
    except KeyError:
        print(f"Неизвестный день недели: {day_name}")
        return None  # Возвращаем None, если день не найден


# Команда для регистрации тренировки
@bot.message_handler(commands=['done'])
def mark_training_done(message):
    user_data = data_store[str(message.chat.id)]
    user_data['training_history'].append({
        'date': str(datetime.date.today()),
        'status': 'выполнено'
    })
    data_store[str(message.chat.id)] = user_data
    bot.reply_to(message, "Тренировка успешно отмечена как выполненная.")


# Команда для просмотра истории тренировок
@bot.message_handler(commands=['history'])
def show_training_history(message):
    user_data = data_store[str(message.chat.id)]
    history = user_data.get('training_history', [])

    if history:
        history_message = '\n'.join([f"{item['date']}: {item['status']}" for item in history])
        bot.send_message(message.chat.id, f"История тренировок:\n{history_message}")
    else:
        bot.send_message(message.chat.id, "Пока нет записей о тренировках.")

#Команда для вывода дополнительной информации
@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """
    Дополнительная информация, которая поможет сделать тренировки интереснее и разнообразнее:

    1. **Введение прогрессии нагрузки**:
    - Постепенное увеличение веса: Еженедельно или раз в две недели увеличивайте рабочий вес на 2-5% для силовых упражнений.
    - Увеличение числа повторений: Постепенно увеличивайте количество повторений в подходах.
    - Усложнение упражнений: По мере роста силы добавляйте новые, более сложные упражнения.

    2. **Разнообразие упражнений**:
    - Альтернативные упражнения: Для каждой мышечной группы есть множество упражнений. Например, вместо жима штанги лежа можно делать жим гантелей под углом или отжимания на брусьях.
    - Суперсеты и дроп-сеты: Сочетайте упражнения для разных мышечных групп или выполняйте несколько подходов подряд с уменьшением веса для усиления интенсивности.

    3. **Включение активного отдыха**:
    - Кардио: Включите различные виды кардио тренировок (бег, велосипед, плавание) для улучшения сердечно-сосудистой системы.
    - Растяжка: После каждой тренировки выполняйте комплекс растяжки для улучшения гибкости и предотвращения травм.

    4. **Добавление функциональных тренировок**:
    - Включение упражнений, имитирующих повседневные движения: Это сделает тренировки более интересными и полезными для повседневной жизни.
    """
    bot.reply_to(message, help_text)


# Обработка ошибок при работе с polling
try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Ошибка в polling: {str(e)}")


# Закрываем хранилище данных при завершении работы
data_store.close()