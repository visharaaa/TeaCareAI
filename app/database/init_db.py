from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.database.db import Database



#params=>none
#this function will be called to create a new database
def create_postgres_db(default_db,new_db):
    # Connect to the default 'postgres' database

    conn = Database(database=default_db).conn

    # PostgreSQL requires 'autocommit' to be turned on to create a database
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # 2. Execute the creation command
        cursor.execute(f"CREATE DATABASE {new_db};")
        print(f"Database '{new_db}' created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        cursor.close()
        conn.close()

#params=>none
#this function will be called to initialize the database
#it will create a new database and create tables and add testing data
def init_db(default_db,new_db,create_tables_path,test_data_path):
    try:
        create_postgres_db(default_db,new_db)
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    database=Database()
    database.create_tables(create_tables_path)
    database.add_dummimg_data(test_data_path)
    print("Database initialized successfully!")

