"""
This script is part of a Telegram bot designed to manage user interactions related
to projects. It provides functionality for navigating through a project selection
menu, viewing detailed project information, and registering for projects. The script
leverages the python-telegram-bot library's asynchronous capabilities to manage
conversations and user interactions effectively.
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


async def projects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Display the sub-menu for projects when the user selects the 'Projects' option.

    This function sends a message to the user with a greeting and a list of
    available projects, each represented as an inline keyboard button. A 'Back'
    button is also included to allow the user to return to the previous menu.

    Args:
        update (Update): Incoming update object containing the user's message and data.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating that the bot is now in the project menu.
    """
    await update.message.reply_text(
        gl.TEXT_DATA["project_greetings"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [[InlineKeyboardButton(button, callback_data=button)]
                for button in gl.PROJECT_MENU_BUTTONS]
    keyboard.append([InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=gl.TEXT_DATA["project_menu"],
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.PROJECT_MENU


async def project_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user selections from the project sub-menu.

    Depending on the user's selection, this function either displays detailed
    information about a selected project or navigates back to the previous menu.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, such as showing project information or returning to the menu.
    """
    query = update.callback_query
    await query.answer()

    match query.data:
        case gl.PROJECT_MENU_BUTTONS.portfolio:
            return await handle_project_option(update, context, text=gl.TEXT_DATA["project_info"]["portfolio"])
        case gl.PROJECT_MENU_BUTTONS.bots_trading:
            return await handle_project_option(update, context, text=gl.TEXT_DATA["project_info"]["bots_trading"])
        case gl.BACK_BUTTON_NAME:
            return await start(query, context)


async def handle_project_option(update: Update, context: ContextTypes.DEFAULT_TYPE, text) -> int:
    """
    Display project information and provide options to register or go back.

    This function sends a message with the detailed information about a selected
    project and presents the user with an option to register for the project or
    go back to the project menu.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.
        text (str): The project information text to be displayed.

    Returns:
        int: The state indicating that the bot is now showing project information.
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
    return gl.PROJECT_INFO_MENU


async def project_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the back button or registration callback in the project information menu.

    This function checks whether the user wants to go back to the project menu or
    proceed with registration for a selected project.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, such as returning to the project menu or proceeding with registration.
    """
    query = update.callback_query
    await query.answer()

    if query.data == gl.BACK_BUTTON_NAME:
        return await projects_menu(query, context)
    elif query.data == gl.REGISTRATION_CALLBACK:
        return await reg.register(query, context, gl.REGISTRATION_FOR_PROJECT)
