import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
NEW_DB_NAME = ""

def create_postgres_db():
    # Connect to the default 'postgres' database
    conn = psycopg2.connect(
        host=DB_HOST,
        database="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
    )

    # PostgreSQL requires 'autocommit' to be turned on to create a database
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # 2. Execute the creation command
        cursor.execute(f"CREATE DATABASE {NEW_DB_NAME};")
        print(f"Database '{NEW_DB_NAME}' created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        cursor.close()
        conn.close()

from db_credentials import create_db_connection

def create_tables():
    with open('./create_tables.sql', 'r') as file:
        sql_script = file.read()

    # Connect to the database
    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        # Execute the entire script as one string
        cursor.execute(sql_script)
        conn.commit()
        print("Script executed successfully!")
    except Exception as e:
        conn.rollback()  # Roll back on error
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_postgres_db()
    create_tables()