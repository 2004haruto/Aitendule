import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        host=os.getenv("MYSQL_HOST", "mysql2"),  # docker-composeのサービス名を使う
        database=os.getenv("MYSQL_DB", "AI_Seminar_IE3B"),
        port=int(os.getenv("MYSQL_PORT", "3308")),
        charset="utf8mb4"
    )
