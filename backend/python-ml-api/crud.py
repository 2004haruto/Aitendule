from db import get_connection

def get_latest_location(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_locations WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
    location = cursor.fetchone()
    conn.close()
    return location

def get_clothing_choices(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_clothing_choices WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_clothing_items():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clothing_items")
    data = cursor.fetchall()
    conn.close()
    return data
