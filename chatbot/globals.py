import os
import json

import pytz

from collections import namedtuple

__version__ = "1.0"

TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
DB_FILE = "dynamic/bots_info.db"
BASE_PATH = "dynamic/"
SEPERATOR = "|"

# Define states
START_MENU, COURSES_MENU, COURSE_INFO_MENU, \
    ASK_NAME, ASK_NUMBER, ASK_CITY, ASK_EMAIL, CONFIRMATION, \
    WEBINAR_MENU, PROJECT_MENU, PROJECT_INFO_MENU,\
    FINISH_REGISTRATION, SET_WEBINAR, SET_WEBINAR_URL, WAITING_FOR_MESSAGE,\
    REVIEW_SCHEDULE, WAITING_FOR_TIME = range(17)

# Define buttons names
Start_buttons = namedtuple("Start_buttuns", ["courses", "projects", "webinars", "registration", "cancel"])
START_KEYBOARD_BUTTONS = Start_buttons("Навчання", "Проекти", "Вебінари", "Запис на консультацію", "Завершити розмову")
SEND_ALL_BUTTON = "Відправити всім"

Courses_buttons = namedtuple("Courses_buttuns", ["basic", "individual",
                                                 "professional", "cryptocurrency_training",
                                                 "stock_market_training", "investor"]
                             )
COURSES_MENU_BUTTONS = Courses_buttons("Базовий", "Індивідуальний VIP-курс",
                                       "Профі-курс", "Крипто-курс",
                                       "Фондовий ринок", "Курс інвестора")

Project_buttons = namedtuple("Project_buttons", ["portfolio", "bots_trading", "spiceprop"])
PROJECT_MENU_BUTTONS = Project_buttons("Інвестиційний портфель", "Торгові Роботи", "Spiceprop")

Registration_names = namedtuple("Registration_names", ["registration", "cancel", "registration_webinar"])
REGISTRATION_NAMES = Registration_names("Записатись на консультацію", "Скасувати запис на консультацію",
                                        "Записатись на вебінар")

REGISTRATION_FOR_CONSULTATION, REGISTRATION_FOR_WEBINAR, REGISTRATION_FOR_PROJECT, REGISTRATION_FOR_COURSE = \
    "Консультація", "Вебінар", "Проект", "Навчання"

BACK_BUTTON_NAME = "Назад"
PHONE_BUTTON_NAME = "Поширити номер телефону"
YES_BUTTON_NAME = "Так"
NO_BUTTON_NAME = "Ні"
STOP_BUTTON = "Зупинити"
CONFIRM_SET_TIME_BUTTON = "Підтвердити та встановити час"
START_OVER_BUTTON = "Почати спочатку"

REGISTRATION_CALLBACK = "201"
CANCEL_REGISTRATION_CALLBACK = "-1"

# Webinar config
HOURS_REMIND = 1
SET_WEBINAR_BUTTON = "Вказати дату вебінару"
TIMEZONE = pytz.timezone("Europe/Kyiv")  # Replace with your timezone

# Static texts.
PATH_TO_JSON_FILE = "static/texts.json"
with open(PATH_TO_JSON_FILE, "r") as text:
    TEXT_DATA = json.load(text)
