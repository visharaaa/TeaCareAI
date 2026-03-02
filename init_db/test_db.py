from db_credentials import create_db_connection

def testing_db():
    with open('./test_data.sql', 'r') as file:
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

if __name__ == "__main__":
    testing_db()
