import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def run_query(sql_query):
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'inten'),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }

    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return [list(row) for row in results]

    except mysql.connector.Error as err:
        print("❌ MySQL error:", err)
        return []

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
