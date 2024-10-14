from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ContextTypes,
)

import chatbot.globals as gl
from chatbot.start import start
from chatbot.registration import finish_registration_menu


async def affiliate_program_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        gl.TEXT_DATA["affiliate_program_greetings"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [
        [InlineKeyboardButton(gl.BACK_BUTTON_NAME, callback_data=gl.BACK_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=gl.TEXT_DATA["affiliate_program_info"],
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return gl.AFFILIATE_PROGRAM_INFO_MENU


async def affiliate_program_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    """
    query = update.callback_query
    await query.answer()
    if query.data == gl.BACK_BUTTON_NAME:
        return await start(query, context)
    return await finish_registration_menu(query, context)
