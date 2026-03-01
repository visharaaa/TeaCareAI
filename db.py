import psycopg2
from db_credentials import create_db_connection
from werkzeug.security import generate_password_hash


def test_db_connection():
    try:
        conn = create_db_connection()
        cur = conn.cursor()
        
        # Test query to see if it works!
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        
        cur.close()
        conn.close()
        return f"Successfully connected to the database! PostgreSQL version: {db_version}"
    except Exception as e:
        return f"Database connection failed: {e}"




#params=>user_id, user_name, email, plain_password, user_type
# add_new_user(1002, "Sharuna", "sharuna@test.com", "my_secret_password", "Admin")
# this function will be called when a new user is being registered. 
# It will take the plain password, hash it securely, and then store the hashed password in the database along with the other user details.
def add_new_user(user_id, user_name, email, plain_password, user_type):
    """
    Inserts a new user into the database securely.
    Returns True if successful, False if it fails.
    """
    # Encrypt the password! 
    hashed_password = generate_password_hash(plain_password)
    
    cur = conn.cursor()
    
    try:
        # The SQL query using %s placeholders for security
        insert_query = """
            INSERT INTO users (user_id, user_name, email, password, user_type)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        # Execute the query with the actual variables
        cur.execute(insert_query, (user_id, user_name, email, hashed_password, user_type))
        
        # Commit (save) the changes to the database
        conn.commit()
        print(f"Success: User '{user_name}' was added to the database!")
        return True
        
    except psycopg2.IntegrityError as e:
        # This catches errors like trying to use an email or user_id that already exists
        conn.rollback() # Undo the broken transaction
        print(f"Database Error: A user with that ID or Email already exists.")
        return False
        
    except Exception as e:
        # Catch any other random errors
        conn.rollback()
        print(f"An unexpected error occurred: {e}")
        return False
        
    finally:
        #close the connection
        cur.close()
        conn.close()




conn=create_db_connection()
print(test_db_connection())
add_new_user(1002, "Sharuna", "sharuna@test.com", "my_secret_password", "Admin")