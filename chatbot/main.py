"""
Telegram Bot Script for CBT

This script implements a Telegram bot using Python and the python-telegram-bot library.
It handles user interactions through a series of menus, allowing users to register for
consultations, view courses, webinars, and projects. The bot uses an asynchronous
architecture to handle multiple conversations and state transitions.
"""
import logging

from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

import chatbot.globals as gl
import chatbot.courses as courses
import chatbot.registration as reg
import chatbot.webinars as webinars
import chatbot.projects as projects
from chatbot.start import start, stop

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the selection of an option in the main menu.

    Depending on the user's selection, navigate to the corresponding menu or action:
    - Courses menu
    - Registration for consultation
    - Webinars menu
    - Projects menu
    - Cancel the current operation
    - Set the webinar date

    Args:
        update (Update): Incoming update object containing message and user data.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow.
    """
    user_option = update.message.text

    match user_option:
        case gl.START_KEYBOARD_BUTTONS.courses:
            return await courses.courses_menu(update, context)
        case gl.START_KEYBOARD_BUTTONS.registration:
            return await reg.register(update, context, gl.REGISTRATION_FOR_CONSULTATION)
        case gl.START_KEYBOARD_BUTTONS.webinars:
            return await webinars.webinars_menu(update, context)
        case gl.START_KEYBOARD_BUTTONS.projects:
            return await projects.projects_menu(update, context)
        case gl.START_KEYBOARD_BUTTONS.cancel:
            return await stop(update, context)
        case gl.SET_WEBINAR_BUTTON:
            return await webinars.set_webinar_date(update, context)


def main() -> None:
    """
    Set up and start the Telegram bot application.

    This function creates an application instance, sets up conversation handlers
    with different states for handling user interactions, and starts the bot's
    polling mechanism to listen for incoming updates and commands.
    """
    application = ApplicationBuilder().token(gl.TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            gl.START_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler)],
            gl.COURSES_MENU: [CallbackQueryHandler(courses.courses_handler)],
            gl.COURSE_INFO_MENU: [CallbackQueryHandler(courses.course_info_handler)],
            gl.ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg.registration_phone),
                          CallbackQueryHandler(reg.registration_phone)],
            gl.ASK_NUMBER: [MessageHandler(filters.CONTACT, reg.registration_city)],
            gl.ASK_CITY: [MessageHandler(filters.TEXT, reg.registration_email)],
            gl.ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg.registration_confirmation)],
            gl.CONFIRMATION: [CallbackQueryHandler(reg.registration_confirmation_handler)],
            gl.WEBINAR_MENU: [CallbackQueryHandler(webinars.webinars_handler)],
            gl.PROJECT_MENU: [CallbackQueryHandler(projects.project_handler)],
            gl.PROJECT_INFO_MENU: [CallbackQueryHandler(projects.project_info_handler)],
            gl.FINISH_REGISTRATION: [CallbackQueryHandler(reg.finish_registration_handler)],
            gl.SET_WEBINAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, webinars.registration_webinar),
                             CallbackQueryHandler(webinars.registration_webinar)]

        },
        fallbacks=[CommandHandler('cancel', stop)],
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    application.run_polling()


if __name__ == '__main__':
    main()
