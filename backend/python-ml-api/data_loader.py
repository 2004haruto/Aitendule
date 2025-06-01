from db import get_connection

def load_training_data():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_clothing_choices")
        choices = cursor.fetchall()

        cursor.execute("SELECT * FROM clothing_items")
        items = cursor.fetchall()

        return choices, items
    finally:
        conn.close()

def get_latest_location(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user_locations WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1",
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def get_clothing_choices(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user_clothing_choices WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def get_clothing_items():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clothing_items")
        return cursor.fetchall()
    finally:
        conn.close()

def get_clothing_item(item_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM clothing_items WHERE id = %s",
            (item_id,)
        )
        return cursor.fetchone()
    finally:
        conn.close()
