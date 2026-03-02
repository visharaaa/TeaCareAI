import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_USER = "postgres"
DB_PASSWORD = "" #change this to your password
DB_HOST = "localhost"
DB_PORT = "5432"
NEW_DB_NAME = "tea_disease_detection_system" #change this to your new database name

#params=>none
#this function will be called to create a new database
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


#params=>none
#this function will be called to create tables in the database
def create_tables():
    with open('./init_db/create_tables.sql', 'r') as file:
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

#params=>none
#this function will be called to add testing data to the database
def add_dummimg_data():
    with open('./init_db/test_data.sql', 'r') as file:
        sql_script = file.read()

    # Connect to the database
    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        # Execute the entire script as one string
        cursor.execute(sql_script)
        conn.commit()
        print("add testing data successfully!")
    except Exception as e:
        conn.rollback()  # Roll back on error
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()



create_postgres_db()
create_tables()
add_dummimg_data()