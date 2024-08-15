"""
This script is a part of a Telegram bot that manages the start and stop of user
interactions and sets reminders for events such as webinars. It includes functionality
to display the main menu, handle the termination of conversations, and schedule reminder
notifications.
"""
import datetime

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

import chatbot.globals as gl


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the bot and display the main menu to the user.

    This function initializes the bot's interaction with the user by sending a
    greeting message and displaying the main menu with available options. It
    also checks if the user is an admin and, if so, adds an additional admin-specific
    button to the menu.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating that the bot is now in the main menu.
    """
    keyboard_buttons = [[button] for button in gl.START_KEYBOARD_BUTTONS]
    chat_id = update.message.chat_id
    if chat_id == int(gl.ADMIN_CHAT_ID):
        keyboard_buttons.append([gl.SET_WEBINAR_BUTTON])
    reply_markup = ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        gl.TEXT_DATA["greetings"],
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.START_MENU


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel and end the conversation.

    This function sends a goodbye message to the user and removes the keyboard
    from the chat, signaling the end of the conversation.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating the end of the conversation.
    """
    await update.message.reply_text(gl.TEXT_DATA["goodbye"], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def make_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Schedule a reminder for an upcoming event (e.g., a webinar).

    This function calculates the time for a reminder notification based on the
    event's date and time, then schedules a job to send this reminder message
    to the user at the appropriate time.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.
    """
    chat_id = update.effective_message.chat_id
    date_obj = datetime.datetime.strptime(gl.WEBINAR_DATE, "%d.%m.%Y %H:%M") - datetime.timedelta(hours=gl.HOURS_REMIND)
    date_obj = gl.TIMEZONE.localize(date_obj)  # Localize the datetime to your timezone
    context.job_queue.run_once(alarm, when=date_obj, chat_id=chat_id, name=str(chat_id))


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send the alarm message to the user.

    This function is triggered by a scheduled job to send a reminder message
    to the user about an upcoming event.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Context object containing job data and bot information.
    """
    job = context.job
    text = gl.TEXT_DATA["webinar_reminder"].format(gl.HOURS_REMIND)
    await context.bot.send_message(job.chat_id, text=text)


def remove_all_jobs(context):
    """
    Remove all jobs from the job queue.

    This function retrieves all currently scheduled jobs in the job queue and
    schedules each one for removal, effectively canceling them.

    Args:
        context (telegram.ext.CallbackContext): The context object containing the job queue.
    """
    jobs = context.job_queue.jobs()

    # Iterate over the jobs and remove each one
    for job in jobs:
        job.schedule_removal()
