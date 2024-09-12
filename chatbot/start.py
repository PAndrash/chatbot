"""
This script is a part of a Telegram bot that manages the start and stop of user
interactions and sets reminders for events such as webinars. It includes functionality
to display the main menu, handle the termination of conversations, and schedule reminder
notifications.
"""
import datetime

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler

import chatbot.globals as gl
from db.database import insert_user, \
    get_webinars_info, get_all_scheduled_messages, \
    get_all_chat_ids_from_db, delete_scheduled_message_by_time, \
    insert_webinar_user, get_future_webinars_and_delete_past


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
    if chat_id != int(gl.ADMIN_CHAT_ID):
        insert_user(chat_id)

    if chat_id == int(gl.ADMIN_CHAT_ID):
        keyboard_buttons.append([gl.SET_WEBINAR_BUTTON])
        keyboard_buttons.append([gl.SEND_ALL_BUTTON])
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
    webinar_data, webinar_url = get_webinars_info()
   # date_obj = datetime.datetime.strptime(webinar_data, "%d.%m.%Y %H:%M") - datetime.timedelta(hours=gl.HOURS_REMIND)
    date_obj = datetime.datetime.strptime(webinar_data, "%d.%m.%Y %H:%M")
    date_obj = gl.TIMEZONE.localize(date_obj)  # Localize the datetime to your timezone
    insert_webinar_user(chat_id, date_obj, webinar_url)
    context.job_queue.run_once(webinar_reminder, data=webinar_url, when=date_obj, chat_id=chat_id, name=str(chat_id))


async def webinar_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send the alarm message to the user.

    This function is triggered by a scheduled job to send a reminder message
    to the user about an upcoming event.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Context object containing job data and bot information.
    """
    job = context.job
    text = gl.TEXT_DATA["webinar_reminder"].format(gl.HOURS_REMIND, job.data)
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


def restore_all_jobs(application) -> None:
    users = get_all_chat_ids_from_db()
    all_scheduled_messages = get_all_scheduled_messages()
    for user in users:
        for message in all_scheduled_messages:
            scheduled_time = message[0]
            date_obj = datetime.datetime.strptime(scheduled_time, "%d.%m.%Y %H:%M")
            date_obj = gl.TIMEZONE.localize(date_obj)  # Localize the datetime to your timezone
            now = datetime.datetime.now(gl.TIMEZONE)
            if now > date_obj:
                delete_scheduled_message_by_time(scheduled_time)
                continue

            application.job_queue.run_once(send_message,
                                           data=message,
                                           when=date_obj,
                                           chat_id=user,
                                           name=str(user))


async def send_message(application):
    message = application.job.data

    text_messages, photo_messages = message[1].split(gl.SEPERATOR), message[2].split(gl.SEPERATOR)
    for message in text_messages:
        await application.bot.send_message(chat_id=application.job.chat_id, text=message)

    if photo_messages:
        media_group = [InputMediaPhoto(media=msg) for msg in photo_messages]
        await application.bot.send_media_group(chat_id=application.job.chat_id, media=media_group)


def restore_all_webinars(application) -> None:
    webinars_info = get_future_webinars_and_delete_past()
    for info in webinars_info:
        user_chat_id, webinar_data, webinar_url = info
        webinar_data = datetime.datetime.fromisoformat(webinar_data)
        application.job_queue.run_once(webinar_reminder,
                                       data=webinar_url,
                                       when=webinar_data,
                                       chat_id=user_chat_id,
                                       name=str(user_chat_id))

