"""
This script is a part of a Telegram bot designed to manage user registration processes
for various services, such as courses, webinars, and projects. It facilitates the
collection of user information, including their name, phone number, city, and email,
and sends this data to the admin for processing. The script utilizes the
python-telegram-bot library's asynchronous capabilities to handle user interactions
seamlessly.
"""
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler
)

import chatbot.globals as gl
from chatbot.start import start, make_reminder


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE, registration_for: str) -> int:
    """
    Initiate the registration process by asking the user for their name.

    This function starts the registration process by storing the purpose of
    the registration (e.g., for a webinar or a project) and prompts the user
    to provide their name.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.
        registration_for (str): The type of registration being conducted (e.g., for a webinar or project).

    Returns:
        int: The next state in the conversation flow, indicating that the bot is now asking for the user's name.
    """
    keyboard = [
        [InlineKeyboardButton(gl.REGISTRATION_NAMES.cancel, callback_data=gl.CANCEL_REGISTRATION_CALLBACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data["registration_for"] = registration_for
    await update.message.reply_text(gl.TEXT_DATA["registration_question"]["name"],
                                    reply_markup=reply_markup,
                                    parse_mode="HTML")
    return gl.ASK_NAME


async def registration_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Store the user's name and ask for their phone number.

    This function stores the name provided by the user and then prompts them
    to share their phone number using a keyboard button that requests contact
    information.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, indicating that the bot is now asking for the user's phone number.
    """
    query = update.callback_query
    await query.answer()
    if query.data == gl.CANCEL_REGISTRATION_CALLBACK:
        return await finish_registration_menu(query, context)

    context.user_data['name'] = update.message.text
    reply_markup = ReplyKeyboardMarkup([[
        KeyboardButton(gl.PHONE_BUTTON_NAME, request_contact=True)
    ]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(gl.TEXT_DATA["registration_question"]["phone"],
                                    reply_markup=reply_markup,
                                    parse_mode="HTML")
    return gl.ASK_NUMBER


async def registration_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Store the user's phone number and ask for their city.

    This function stores the phone number provided by the user and then prompts
    them to enter their city.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, indicating that the bot is now asking for the user's city.
    """
    context.user_data['phone_number'] = update.message.contact.phone_number
    await update.message.reply_text(gl.TEXT_DATA["registration_question"]["city"], reply_markup=ReplyKeyboardRemove())
    return gl.ASK_CITY


async def registration_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Store the user's city and ask for their email address.

    This function stores the city provided by the user and then prompts them
    to enter their email address.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, indicating that the bot is now asking for the user's email address.
    """
    context.user_data['city'] = update.message.text
    await update.message.reply_text(gl.TEXT_DATA["registration_question"]["email"], reply_markup=ReplyKeyboardRemove())
    return gl.ASK_EMAIL


async def registration_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
   Confirm the registration details with the user before submission.

   This function stores the email provided by the user and then displays a
   summary of all the collected information, asking the user to confirm its
   accuracy before submitting it.

   Args:
       update (Update): Incoming update object containing the user's message.
       context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

   Returns:
       int: The next state in the conversation flow, indicating that the bot is now asking for confirmation of the details.
   """
    context.user_data["email"] = update.message.text
    name = context.user_data["name"]
    phone_number = context.user_data["phone_number"]
    city = context.user_data["city"]
    email = context.user_data["email"]

    keyboard = [
        [InlineKeyboardButton(gl.YES_BUTTON_NAME, callback_data=gl.YES_BUTTON_NAME)],
        [InlineKeyboardButton(gl.NO_BUTTON_NAME, callback_data=gl.NO_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"{gl.TEXT_DATA['registration_question']['confirmation']}Ім'я: {name}\n" \
              f"Номер телефону: {phone_number}\nМісто: {city}\nEmail: {email}"
    await update.message.reply_text(message,
                                    reply_markup=reply_markup,
                                    parse_mode="HTML")
    return gl.CONFIRMATION


async def registration_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's confirmation and send registration data to the admin.

    If the user confirms the registration details, this function sends the
    information to the admin and ends the conversation. If the user chooses not
    to confirm, it restarts the registration process.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, either ending the conversation or restarting the registration process.
    """
    query = update.callback_query
    await query.answer()
    if query.data == gl.YES_BUTTON_NAME:
        admin_chat_id = gl.ADMIN_CHAT_ID  # Replace with your admin chat ID
        name = context.user_data["name"]
        phone_number = context.user_data["phone_number"]
        city = context.user_data["city"]
        email = context.user_data["email"]
        registration_for = context.user_data["registration_for"]

        message = f"{gl.TEXT_DATA['registration_question']['admin']}Тип: {registration_for}\nІм'я: {name}\n" \
                  f"Номер телефону: {phone_number}\nМісто: {city}\nEmail: {email}"
        await context.bot.send_message(chat_id=admin_chat_id, text=message)

        await query.message.reply_text(gl.TEXT_DATA["registration_question"]["goodbye"])
        if registration_for == gl.REGISTRATION_FOR_WEBINAR:
            await make_reminder(update, context)

        return await finish_registration_menu(query, context)
    else:
        return await register(query, context)  # Restart the process if not confirmed


async def finish_registration_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Display a final prompt asking if the user wants to start a new registration.

    This function sends a message asking the user if they want to start a new
    registration process or finish the current session.

    Args:
        update (Update): Incoming update object containing the user's message.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The state indicating that the bot is asking the user whether to start a new registration.
    """
    keyboard = [
        [InlineKeyboardButton(gl.YES_BUTTON_NAME, callback_data=gl.YES_BUTTON_NAME)],
        [InlineKeyboardButton(gl.NO_BUTTON_NAME, callback_data=gl.NO_BUTTON_NAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(gl.TEXT_DATA["goodbye_question"], reply_markup=reply_markup)
    return gl.FINISH_REGISTRATION


async def finish_registration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's choice to either start a new registration or end the conversation.

    If the user chooses to start a new registration, this function restarts the
    process. If the user chooses to end the conversation, it sends a goodbye message
    and ends the conversation.

    Args:
        update (Update): Incoming update object containing the user's callback query.
        context (ContextTypes.DEFAULT_TYPE): Context object to maintain data across user sessions.

    Returns:
        int: The next state in the conversation flow, either restarting the registration process or ending the conversation.
    """
    query = update.callback_query
    await query.answer()
    if query.data == gl.YES_BUTTON_NAME:
        return await start(query, context)
    else:
        await update.callback_query.message.reply_text(
            text=gl.TEXT_DATA["goodbye"],
        )
        return ConversationHandler.END




