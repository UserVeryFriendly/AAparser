import telegram
import time
import os
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
from selenium import webdriver

load_dotenv()


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
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
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
    if len(numbers) != 29:
        raise ValueError("Количество чисел должно быть 29")

    table = f"""
    ~~~Запад~~~

    Кожа:
Кладбище {numbers[0]:<10}
Нагорье {numbers[1]:<10}
Коса {numbers[2]:<10}
ДЦП {numbers[3]:<10}

    Ткань:
Мэрианхольд {numbers[4]:<10}
Лилиот {numbers[5]:<10}
Две короны {numbers[6]:<10}
Золотые равнины {numbers[7]:<10}

    Слиток железа:
Згк {numbers[8]:<10}
Морозная гряда {numbers[9]:<10}
Ппз {numbers[10]:<10}

    Строительная древесина:
Гвинедар {numbers[11]:<10}
Солрид {numbers[12]:<10}
Белый лес {numbers[13]:<10}
Заболоты {numbers[14]:<10}

    ~~~Восток~~~

    Кожа:
Махадеби {numbers[15]:<10}
Поющая земля {numbers[16]:<10}
Саванна {numbers[17]:<10}
Рокочка {numbers[18]:<10}

    Ткань:
Радужные пески {numbers[19]:<10}
Псо {numbers[20]:<10}

    Слиток железа:
Полуостров Рассвета {numbers[21]:<10}
Багровый каньон {numbers[22]:<10}
Тигриный хребет {numbers[23]:<10}
Долина талых снегов {numbers[24]:<10}

    Строительная древесина:
Руины харихаралы {numbers[25]:<10}
Инистра {numbers[26]:<10}
Хазира {numbers[27]:<10}
Древний лес {numbers[28]:<10}

С любовью, Хэбпс!(@Snitch151)
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=table
    )


updater = Updater(
    token=os.environ.get('SECRET_BOT_TOKEN'),
    use_context=True
)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, button))

updater.start_polling()
updater.idle()
