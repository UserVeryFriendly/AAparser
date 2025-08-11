import time
import os
import logging
from typing import List
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

send_counter = 0

SLUG = {
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


def start(update: Update, context: CallbackContext) -> None:
    buttons = []
    for server_name in SLUG:
        button = KeyboardButton(text=server_name)
        buttons.append([button])
    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=False, resize_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='''
Пожалуйста не спамьте выбор.
Обработка идет около 5 секунд.
Выберите сервер:
        ''',
        reply_markup=keyboard
    )


def button(update: Update, context: CallbackContext) -> None:
    server_name = update.message.text
    server_id = SLUG.get(server_name)
    if server_id:
        url = f'https://gisaa.ru/veksel/{server_id}'
        get_html_content(url, update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Неверный выбор сервера. Пожалуйста, выберите из списка.'
        )


def get_html_content(url: str, update: Update, context: CallbackContext) -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        # Ждем появления нужных элементов вместо sleep
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.row__cell-max'))
        )
        html = driver.page_source
        extract_numbers(html, update, context)
    except Exception as exc:
        logger.exception("Ошибка при загрузке страницы: %s", exc)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Не удалось загрузить данные. Попробуйте позже.'
        )
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def extract_numbers(html: str, update: Update, context: CallbackContext) -> None:
    html_content = BeautifulSoup(html, 'html.parser')
    td_values = html_content.find_all('td', class_='row__cell-max')
    td_values = td_values[:29]
    if td_values:
        numbers: List[int | str] = []
        for td in td_values:
            text = td.get_text(strip=True)
            if text.isdigit():
                number = int(text)
                numbers.append(number)
            else:
                numbers.append(text)
        generate_table(numbers, update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Значения не были найдены.'
        )


def generate_table(numbers: List[int | str], update: Update, context: CallbackContext) -> None:
    global send_counter
    current_time = time.time()
    formatted_time = time.strftime(
        '%d.%m.%Y %H:%M:%S',
        time.localtime(current_time)
    )

    if len(numbers) != 29:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Ошибка: количество значений отличается от ожидаемого.'
        )
        logger.warning("Ожидалось 29 значений, получено: %s", len(numbers))
        return

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


def main() -> None:
    token = os.environ.get('SECRET_BOT_TOKEN')
    if not token:
        logger.error('SECRET_BOT_TOKEN is not set in environment variables')
        raise RuntimeError('SECRET_BOT_TOKEN is not set')

    updater = Updater(
        token=token,
        use_context=True
    )
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
