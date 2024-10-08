"""
This script is a component of a Telegram bot designed to handle interactions related
to webinars. It provides functionality for displaying webinar information, handling
user registrations, and allowing an admin to set the webinar date.
"""
import datetime

from db.database import get_webinar_data, set_webinar_data, delete_webinar_data

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
from chatbot.start import start, remove_all_jobs
import chatbot.registration as reg


async def webinars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display the webinar menu to the user.

    This function checks if a webinar date is set. If not, it informs the user that
    no webinar is currently planned. Otherwise, it displays the webinar information
    and provides options for registration or returning to the previous menu.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating the bot is now in the webinar menu, or None if no webinar is planned.
    """
    webinar_data = get_webinar_data()
    if not webinar_data:
        await update.message.reply_text(
            gl.TEXT_DATA["webinar_unplanned"],
            parse_mode="HTML",
        )
        return

    await update.message.reply_text(
        gl.TEXT_DATA["webinar_greetings"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [
        [InlineKeyboardButton(gl.REGISTRATION_NAMES.registration_webinar, callback_data=gl.REGISTRATION_CALLBACK)],
        [InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=webinar_data[0],
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.WEBINAR_MENU


async def webinars_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
     Handle user selections in the webinar menu.

     This function processes the user's selection from the webinar menu. It either
     navigates back to the start menu or proceeds with the registration process
     depending on the user's choice.

     Args:
         update (Update): Incoming update object containing the user's interaction.
         context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

     Returns:
         int: The state indicating the next step in the conversation.
     """
    query = update.callback_query
    await query.answer()
    if query.data == gl.BACK_BUTTON_NAME:
        return await start(query, context)
    elif query.data == gl.REGISTRATION_CALLBACK:
        return await reg.register(query, context, gl.REGISTRATION_FOR_WEBINAR)


async def set_webinar_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Prompt the admin to set or confirm the webinar date.

    This function sends a message to the admin, indicating whether a webinar date
    is currently set or not, and asks for input to set or update the date.

    Args:
        update (Update): Incoming update object containing the admin's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating the bot is now waiting for the webinar date to be set.
    """
    keyboard = [
        [InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    webinar_data = get_webinar_data()

    text = gl.TEXT_DATA["set_webinar_true"].format(webinar_data) if webinar_data \
        else gl.TEXT_DATA["set_webinar_false"]

    await update.message.reply_text(text,
                                    reply_markup=reply_markup,
                                    parse_mode="HTML",)
    return gl.SET_WEBINAR_URL


async def registration_webinar_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        return await start(query, context)

    data = update.message.text
    if data == "-":
        remove_all_jobs(context)
        delete_webinar_data()
        await update.message.reply_text(gl.TEXT_DATA["webinar_remove_date_successful"],
                                        parse_mode="HTML")
        return await reg.finish_registration_menu(update, context)

    context.user_data['url'] = data

    keyboard = [
        [InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(gl.TEXT_DATA["set_webinar_time"],
                                    reply_markup=reply_markup,
                                    parse_mode="HTML",)
    return gl.SET_WEBINAR


async def registration_webinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the admin's input for setting the webinar date.

    This function validates the date format entered by the admin. If valid, it saves
    the date; otherwise, it prompts the admin to enter a valid date.

    Args:
        update (Update): Incoming update object containing the admin's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating the next step, either setting the date or returning to the menu.
    """
    query = update.callback_query
    if query:
        await query.answer()
        return await start(query, context)

    data = update.message.text
    if not is_valid_date(data):
        await update.message.reply_text(gl.TEXT_DATA["webinar_wrong_date"],
                                        parse_mode="HTML")
        return await set_webinar_date(update, context)

    set_webinar_data(data, context.user_data['url'])
    await update.message.reply_text(gl.TEXT_DATA["webinar_set_date_successful"],
                                    parse_mode="HTML")
    return await reg.finish_registration_menu(update, context)


def is_valid_date(date_string: str) -> bool:
    """
    Validate the format of the provided date string.

    This function checks if the date string is in the expected format ("%d.%m.%Y %H:%M").
    If it is, the function returns True; otherwise, it returns False.

    Args:
        date_string (str): The date string to validate.

    Returns:
        bool: True if the date string is valid, False otherwise.
    """
    try:
        # Try to parse the date string with the expected format
        datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        # If parsing fails, the date string is not in the correct format
        return False
