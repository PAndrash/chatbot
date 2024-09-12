import sqlite3
from datetime import datetime

import chatbot.globals as gl


# Connect to the SQLite database (it will create it if it doesn't exist)
def create_db_and_tables():
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Create 'users' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_chat_id INTEGER UNIQUE NOT NULL
    )
    ''')

    # Create 'scheduled_messages' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheduled_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheduled_time TEXT NOT NULL, 
        message TEXT NOT NULL,
        images_ids TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS webinars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        webinar_data TEXT NOT NULL,
        webinar_url TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS webinars_users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_chat_id INTEGER NOT NULL,
           webinar_data DATETIME NOT NULL,
           webinar_url TEXT
       )
    ''')

    conn.commit()
    conn.close()


def insert_user(user_chat_id):
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO users (user_chat_id) 
    VALUES (?)
    ''', (user_chat_id,))

    conn.commit()
    conn.close()


def insert_scheduled_message(scheduled_time, message, image=None):
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO scheduled_messages (scheduled_time, message, images_ids) 
    VALUES (?, ?, ?)
    ''', (scheduled_time, message, image))

    conn.commit()
    conn.close()


def get_all_chat_ids_from_db():
    """
    Extracts all chat IDs from a SQLite database.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of chat IDs.
    """
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Replace 'users' with your actual table name and 'chat_id' with your actual column name
    cursor.execute('SELECT user_chat_id FROM users')
    chat_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return chat_ids


def set_webinar_data(webinar_data, webinar_url):
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Check if a row already exists
    cursor.execute('SELECT COUNT(*) FROM webinars')
    row_count = cursor.fetchone()[0]

    if row_count > 0:
        # Update existing row
        cursor.execute('''
        UPDATE webinars
        SET webinar_data = ?, webinar_url = ?
        ''', (webinar_data, webinar_url))
    else:
        # Insert new row
        cursor.execute('''
        INSERT INTO webinars (webinar_data, webinar_url) 
        VALUES (?, ?)
        ''', (webinar_data, webinar_url))

    conn.commit()
    conn.close()


def get_webinar_data() -> str | None:
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Replace 'users' with your actual table name and 'chat_id' with your actual column name
    cursor.execute('SELECT webinar_data FROM webinars')
    webinar_data = cursor.fetchall()
    if not webinar_data:
        return None

    conn.close()
    return webinar_data.pop()


def delete_webinar_data():
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Delete the row
    cursor.execute('DELETE FROM webinars')

    conn.commit()
    conn.close()


def get_webinars_info():
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Retrieve the data from the 'webinars' table
    cursor.execute('SELECT webinar_data, webinar_url FROM webinars LIMIT 1')
    row = cursor.fetchone()

    conn.close()
    return row


def get_all_scheduled_messages():
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Select all columns and rows from the 'scheduled_messages' table
    cursor.execute('SELECT scheduled_time,message,images_ids FROM scheduled_messages')

    # Fetch all rows from the result set
    rows = cursor.fetchall()

    conn.close()

    # Return the list of rows, where each row is a list of column values
    return rows


def delete_scheduled_message_by_time(scheduled_time):
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Delete the row where 'scheduled_time' matches the provided value
    cursor.execute('''
    DELETE FROM scheduled_messages
    WHERE scheduled_time = ?
    ''', (scheduled_time,))

    conn.commit()
    conn.close()


def insert_webinar_user(user_chat_id, date_obj, webinar_url):
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Insert data into 'webinars_users'
    cursor.execute('''
    INSERT INTO webinars_users (user_chat_id, webinar_data, webinar_url) 
    VALUES (?, ?, ?)
    ''', (user_chat_id, date_obj, webinar_url))

    conn.commit()
    conn.close()


def get_future_webinars_and_delete_past():
    conn = sqlite3.connect(gl.DB_FILE)
    cursor = conn.cursor()

    # Get the current datetime
    now = datetime.now(gl.TIMEZONE)

    # Retrieve all rows where 'webinar_data' is in the future
    cursor.execute('''
    SELECT user_chat_id, webinar_data, webinar_url FROM webinars_users 
    WHERE webinar_data > ?
    ''', (now,))

    future_webinars = cursor.fetchall()

    # Delete rows where 'webinar_data' is in the past
    cursor.execute('''
    DELETE FROM webinars_users 
    WHERE webinar_data <= ?
    ''', (now,))

    conn.commit()
    conn.close()

    # Return the future webinars
    return future_webinars
