import datetime

from telegram import Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes

import chatbot.globals as gl
from chatbot.registration import finish_registration_menu
from chatbot.webinars import is_valid_date
from db.database import insert_scheduled_message, get_all_chat_ids_from_db


async def get_data_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        gl.TEXT_DATA["message_for_all"]["start_message"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data['messages'] = []
    await update.message.reply_text(
        gl.TEXT_DATA["message_for_all"]["beginning"],
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(gl.STOP_BUTTON, callback_data="stop")]])
    )
    return gl.WAITING_FOR_MESSAGE


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives messages or media groups from admin and stores their file IDs."""
    # Check if this is part of a media group
    if update.message.media_group_id:
        file_id = update.message.photo[-1].file_id
        context.user_data['messages'].append({'type': 'photo', 'file_id': file_id})
    else:
        # Handle single images or text messages
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            context.user_data['messages'].append({'type': 'photo', 'file_id': file_id})
        else:
            context.user_data['messages'].append({'type': 'text', 'content': update.message.text})

        # Acknowledge receipt of individual messages or non-group media
        await update.message.reply_text(gl.TEXT_DATA["message_for_all"]["continue"],
                                        reply_markup=InlineKeyboardMarkup(
                                            [[InlineKeyboardButton(gl.STOP_BUTTON, callback_data="stop")]]))

    return gl.WAITING_FOR_MESSAGE


async def stop_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the 'Stop' button press, shows collected messages, and asks for scheduling time."""
    query = update.callback_query
    await query.answer()

    # Display the collected messages for review
    collected_messages = context.user_data.get('messages', [])

    if not collected_messages:
        await query.edit_message_text(gl.TEXT_DATA["message_for_all"]["nothing"])
        return await finish_registration_menu(query, context)

    # Show collected messages
    text_messages = [msg for msg in collected_messages if msg['type'] == 'text']
    photo_messages = [msg for msg in collected_messages if msg['type'] == 'photo']

    # Send all collected text messages
    for message in text_messages:
        await context.bot.send_message(chat_id=query.message.chat_id, text=message['content'])

    # Send photos as a media group if there are any
    if photo_messages:
        media_group = [InputMediaPhoto(media=msg['file_id']) for msg in photo_messages]
        await context.bot.send_media_group(chat_id=query.message.chat_id, media=media_group)

    # Inline buttons to proceed or restart
    review_keyboard = [
        [InlineKeyboardButton(gl.CONFIRM_SET_TIME_BUTTON, callback_data="confirm")],
        [InlineKeyboardButton(gl.START_OVER_BUTTON, callback_data="start_over")]
    ]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=gl.TEXT_DATA["message_for_all"]["confirmation"],
        reply_markup=InlineKeyboardMarkup(review_keyboard)
    )
    return gl.REVIEW_SCHEDULE


async def confirm_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for the scheduling time after confirmation of messages."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(gl.TEXT_DATA["message_for_all"]["time"],
                                  parse_mode="HTML")
    return gl.WAITING_FOR_TIME


async def receive_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the scheduling time and stores the message for later delivery."""
    data = update.message.text

    if not is_valid_date(data):
        await update.message.reply_text(gl.TEXT_DATA["webinar_wrong_date"],
                                        parse_mode="HTML")
        return gl.WAITING_FOR_TIME

    date_obj = datetime.datetime.strptime(data, "%d.%m.%Y %H:%M")
    date_obj = gl.TIMEZONE.localize(date_obj)  # Localize the datetime to your timezone

    await save_to_db(context, data)
    collected_messages = context.user_data.get('messages', [])
    users = get_all_chat_ids_from_db()

    for user in users:
        context.job_queue.run_once(scheduled_msg, data=collected_messages, when=date_obj, chat_id=user, name=str(user))

    return await finish_registration_menu(update, context)


async def restart_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Restarts the message collection process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(gl.TEXT_DATA["message_for_all"]["restart"])
    context.user_data['messages'] = []
    return gl.WAITING_FOR_MESSAGE


async def scheduled_msg(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    text_messages = [msg for msg in job.data if msg['type'] == 'text']
    photo_messages = [msg for msg in job.data if msg['type'] == 'photo']

    for message in text_messages:
        await context.bot.send_message(chat_id=job.chat_id, text=message['content'])

    if photo_messages:
        media_group = [InputMediaPhoto(media=msg['file_id']) for msg in photo_messages]
        await context.bot.send_media_group(chat_id=job.chat_id, media=media_group)


async def save_to_db(context: ContextTypes.DEFAULT_TYPE, data) -> None:
    collected_messages = context.user_data.get('messages', [])
    text_messages = [msg["content"] for msg in collected_messages if msg['type'] == 'text']
    photo_messages = [msg['file_id'] for msg in collected_messages if msg['type'] == 'photo']

    text_messages_single_line = gl.SEPERATOR.join(text_messages)
    photo_messages_single_line = gl.SEPERATOR.join(photo_messages)

    insert_scheduled_message(data, text_messages_single_line, photo_messages_single_line)
