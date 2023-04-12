import telegram
import time
import os
import logging
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

send_counter = 0

slug = {
    'Ария': 33,
    'Ифнир': 49,
    'Каиль': 43,
    'Корвус': 42,
    'Кракен': 48,
    'Луций': 1,
    'Нуи': 44,
    'Ренессанс': 47,
    'Хазе': 35,
    'Шаеда': 46,
    'Фанем': 45
}


def start(update, context):
    buttons = []
    for server_name in slug:
        button = KeyboardButton(
            text=server_name
        )
        buttons.append([button])
    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=False)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='''
Пожалуйста не спамьте выбор.
Обработка идет около 5 секунд.
Выберите сервер:
        ''',
        reply_markup=keyboard
    )


def button(update, context):
    server_name = update.message.text
    server_id = slug.get(server_name)
    if server_id:
        url = f'https://gisaa.ru/veksel/{server_id}'
        get_html_content(url, update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Неверный выбор сервера. Пожалуйста, выберите из списка.'
        )


def get_html_content(url, update, context):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    driver.close()
    extract_numbers(html, update, context)


def extract_numbers(html, update, context):
    html_content = BeautifulSoup(html, 'html.parser')
    td_values = html_content.find_all('td', class_='row__cell-max')
    td_values = td_values[:29]
    if td_values:
        numbers = []
        for td in td_values:
            text = td.get_text(strip=True)
            if text.isdigit():
                number = int(text)
                numbers.append(number)
            else:
                numbers.append(text)
        generate_table(numbers, update, context)
    else:
        raise ValueError("Значения не были найдены.")


def generate_table(numbers, update, context):
    global send_counter
    current_time = time.time()
    formatted_time = time.strftime(
        '%d.%m.%Y %H:%M:%S',
        time.localtime(current_time)
    )

    if len(numbers) != 29:
        raise ValueError("Количество чисел должно быть 29")

    table = f"""
{formatted_time}
    ~~~Запад~~~

    Кожа:
Кладбище {numbers[0]}
Нагорье {numbers[1]}
Коса {numbers[2]}
ДЦП {numbers[3]}

    Ткань:
Мэрианхольд {numbers[4]}
Лилиот {numbers[5]}
Две короны {numbers[6]}
Золотые равнины {numbers[7]}

    Слиток железа:
Згк {numbers[8]}
Морозная гряда {numbers[9]}
Ппз {numbers[10]}

    Строительная древесина:
Гвинедар {numbers[11]}
Солрид {numbers[12]}
Белый лес {numbers[13]}
Заболоты {numbers[14]}

    ~~~Восток~~~

    Кожа:
Махадеби {numbers[15]}
Поющая земля {numbers[16]}
Саванна {numbers[17]}
Рокочка {numbers[18]}

    Ткань:
Радужные пески {numbers[19]}
Псо {numbers[20]}

    Слиток железа:
Полуостров Рассвета {numbers[21]}
Багровый каньон {numbers[22]}
Тигриный хребет {numbers[23]}
Долина талых снегов {numbers[24]}

    Строительная древесина:
Руины харихаралы {numbers[25]}
Инистра {numbers[26]}
Хазира {numbers[27]}
Древний лес {numbers[28]}

С любовью, Хэбпс!(@Snitch151)
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=table
    )
    send_counter += 1
    logging.info(f"Send: {update.effective_user.first_name} {update.effective_user.last_name}, ID: {update.effective_user.id}")
    logger.info(f'Send: {send_counter}')


updater = Updater(
    token=os.environ.get('SECRET_BOT_TOKEN'),
    use_context=True
)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, button))

updater.start_polling()
updater.idle()
