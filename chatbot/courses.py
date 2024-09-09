"""
This script is part of a Telegram bot that manages user interactions related to courses.
It allows users to navigate through a course selection menu, view detailed course information,
and register for courses. The script uses the python-telegram-bot library's asynchronous
functions to manage state transitions and user interactions smoothly.
"""

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    ContextTypes,
)

import chatbot.globals as gl
from chatbot.start import start
import chatbot.registration as reg


async def courses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Display the sub-menu for courses when the user selects the 'Courses' option.

    This function sends a message to the user with a greeting and a list of
    available courses, each represented as an inline keyboard button. A 'Back'
    button is also included to allow the user to return to the previous menu.

    Args:
        update (Update): Incoming update object containing the user's message and data.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating that the bot is now in the course menu.
    """
    await update.message.reply_text(
        gl.TEXT_DATA["courses_greetings"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [[InlineKeyboardButton(button, callback_data=button)]
                for button in gl.COURSES_MENU_BUTTONS]
    keyboard.append([InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=gl.TEXT_DATA["courses_menu"],
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.COURSES_MENU


async def courses_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user selections from the course sub-menu.

    Depending on the user's selection, this function either displays detailed
    information about a selected course or navigates back to the previous menu.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, such as showing course information or returning to the menu.
    """
    query = update.callback_query
    await query.answer()

    match query.data:
        case gl.COURSES_MENU_BUTTONS.basic:
            context.user_data["course"] = gl.COURSES_MENU_BUTTONS.basic
            return await handle_courses_option(update, context, text=gl.TEXT_DATA["courses_info"]["basic"])
        case gl.COURSES_MENU_BUTTONS.individual:
            context.user_data["course"] = gl.COURSES_MENU_BUTTONS.individual
            return await handle_courses_option(update, context, text=gl.TEXT_DATA["courses_info"]["individual"])
        case gl.COURSES_MENU_BUTTONS.professional:
            context.user_data["course"] = gl.COURSES_MENU_BUTTONS.professional
            return await handle_courses_option(update, context, text=gl.TEXT_DATA["courses_info"]["professional"])
        case gl.COURSES_MENU_BUTTONS.cryptocurrency_training:
            context.user_data["course"] = gl.COURSES_MENU_BUTTONS.cryptocurrency_training
            return await handle_courses_option(update, context, text=gl.TEXT_DATA["courses_info"]["cryptocurrency_training"])
        case gl.COURSES_MENU_BUTTONS.stock_market_training:
            context.user_data["course"] = gl.COURSES_MENU_BUTTONS.stock_market_training
            return await handle_courses_option(update, context, text=gl.TEXT_DATA["courses_info"]["stock_market_training"])
        case gl.COURSES_MENU_BUTTONS.investor:
            context.user_data["course"] = gl.COURSES_MENU_BUTTONS.stock_market_training
            return await handle_courses_option(update, context, text=gl.TEXT_DATA["courses_info"]["investor"])
        case gl.BACK_BUTTON_NAME:
            return await start(query, context)


async def handle_courses_option(update: Update, context: ContextTypes.DEFAULT_TYPE, text) -> int:
    """
    Display course information and provide options to register or go back.

    This function sends a message with the detailed information about a selected
    course and presents the user with an option to register for the course or go
    back to the course menu.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.
        text (str): The course information text to be displayed.

    Returns:
        int: The state indicating that the bot is now showing course information.
    """
    keyboard = [
        [InlineKeyboardButton(gl.REGISTRATION_NAMES.registration, callback_data=gl.REGISTRATION_CALLBACK)],
        [InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.COURSE_INFO_MENU


async def course_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the back button or registration callback in the course information menu.

    This function checks whether the user wants to go back to the course menu or
    proceed with registration for a selected course.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, such as returning to the course menu or proceeding with registration.
    """
    query = update.callback_query
    await query.answer()
    text = f"{gl.REGISTRATION_FOR_COURSE} {context.user_data['course']}"
    if query.data == gl.BACK_BUTTON_NAME:
        return await courses_menu(query, context)
    elif query.data == gl.REGISTRATION_CALLBACK:
        return await reg.register(query, context, text)
