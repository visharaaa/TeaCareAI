import psycopg2

DB_USER = "postgres" #Enter your username
DB_PASSWORD = "" #Enter your password
DB_HOST = "localhost" #Enter you host
DB_PORT = "5432"
DB_NAME = "tea_disease_detection_system"


def create_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn
