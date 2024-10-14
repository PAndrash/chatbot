from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    InputMediaPhoto
)

from telegram.ext import (
    ContextTypes,
)

import chatbot.globals as gl
from chatbot.start import start
from chatbot.registration import finish_registration_menu


async def awards_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        gl.TEXT_DATA["awards_greetings"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    chat_id = update.effective_chat.id
    image = gl.TEXT_DATA["awards_image_path"]
    media_group = [InputMediaPhoto(open(image_path, 'rb')) for image_path in gl.get_all_file_paths(image)]
    await context.bot.send_media_group(chat_id=chat_id, media=media_group)

    keyboard = [[InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=gl.TEXT_DATA["awards_info"],
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.AWARDS_MENU


async def awards_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    """
    query = update.callback_query
    await query.answer()
    if query.data == gl.BACK_BUTTON_NAME:
        return await start(query, context)
    return await finish_registration_menu(query, context)

