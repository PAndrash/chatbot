import os
import json

import pytz

from collections import namedtuple

__version__ = "0.1.2"

TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Define states
START_MENU, COURSES_MENU, COURSE_INFO_MENU, \
    ASK_NAME, ASK_NUMBER, ASK_CITY, ASK_EMAIL, CONFIRMATION, \
    WEBINAR_MENU, PROJECT_MENU, PROJECT_INFO_MENU,\
    FINISH_REGISTRATION, SET_WEBINAR = range(13)

# Define buttons names
Start_buttons = namedtuple("Start_buttuns", ["courses", "projects", "webinars", "registration", "cancel"])
START_KEYBOARD_BUTTONS = Start_buttons("Навчання", "Проекти", "Вебінари", "Запис на консультацію", "Завершити розмову")

Courses_buttons = namedtuple("Courses_buttuns", ["basic", "individual",
                                                 "group", "professional", "cryptocurrency_training",
                                                 "stock_market_training"]
                             )
COURSES_MENU_BUTTONS = Courses_buttons("Базовий", "Індивідуальний", "Груповий",
                                       "Професійний", "Навчання по криптовалюті",
                                       "Навчання по фондовому ринку",
                                       )

Project_buttons = namedtuple("Project_buttons", ["portfolio", "bots_trading"])
PROJECT_MENU_BUTTONS = Project_buttons("Інвестиційний портфель", "Торгівля на роботі")

Registration_names = namedtuple("Registration_names", ["registration", "cancel"])
REGISTRATION_NAMES = Registration_names("Зареєструватись", "Скасувати реєстрацію")

REGISTRATION_FOR_CONSULTATION, REGISTRATION_FOR_WEBINAR, REGISTRATION_FOR_PROJECT, REGISTRATION_FOR_COURSE = \
    "Консультація", "Вебінар", "Проект", "Навчання"

BACK_BUTTON_NAME = "Назад"
PHONE_BUTTON_NAME = "Поширити номер телефону"
YES_BUTTON_NAME = "Так"
NO_BUTTON_NAME = "Ні"

REGISTRATION_CALLBACK = "201"
CANCEL_REGISTRATION_CALLBACK = "-1"

# Webinar config
WEBINAR_DATE = ""
HOURS_REMIND = 3
SET_WEBINAR_BUTTON = "Вказати дату вебінару"
TIMEZONE = pytz.timezone("Europe/Kyiv")  # Replace with your timezone

# Static texts.
PATH_TO_JSON_FILE = "/app/texts.json"
with open(PATH_TO_JSON_FILE, "r") as text:
    TEXT_DATA = json.load(text)
