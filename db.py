import psycopg2
from sympy.polys.polyconfig import query

from db_credentials import create_db_connection
from werkzeug.security import generate_password_hash

class Database:
    def __init__(self):
        self.conn = create_db_connection()
        self.cur = self.conn.cursor()

    #params=>none
    #this function will be called to test the database connection
    #it will return the database version if the connection is successful
    #it will return an error message if the connection is not successful
    def test_db_connection(self):
        try:
            self.cur.execute('SELECT version();')
            db_version = self.cur.fetchone()
            return f"Successfully connected! PostgreSQL version: {db_version}"
        except Exception as e:
            return f"Database connection failed: {e}"

    #params=>query, params
    #this function will be called to handle errors when inserting data into the database
    #it will take the query and parameters as a parameter
    def input_error_handler(self, query, params):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            print("Success: Database operation completed.")
            return True
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            print(f"An unexpected error occurred: {e}")
            print("Database Error: A record with that ID/Unique constraint already exists.")
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"An unexpected error occurred: {e}")
            return False
        finally:
            self.cur.close()
            self.cur = self.conn.cursor() 

    #params=>query, params, fetch_all
    #this function will be called to fetch data from the database
    #it will return the data as dictionary if the data is found
    #it will return None if the data is not found
    def fetch_data_handler(self, query, params=None, fetch_all=True):
        try:
            self.cur.execute(query, params or ())
            # Handle cases where query returns no description (like an UPDATE)
            if self.cur.description is None:
                return None
                
            colnames = [desc[0] for desc in self.cur.description]

            if fetch_all:
                rows = self.cur.fetchall()
                return [dict(zip(colnames, row)) for row in rows]
            else:
                row = self.cur.fetchone()
                return dict(zip(colnames, row)) if row else None
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    #params=>user_id, user_name, email, plain_password, user_type
    #this function will be called when a new user is being registered. 
    #It will take the plain password, hash it securely, and then store the hashed password in the database along with the other user details.
    def add_user(self, user_id, user_name, email, plain_password, user_type):
        hashed_password = generate_password_hash(plain_password)
        query = "INSERT INTO users (user_id, user_name, email, password, user_type)VALUES (%s, %s, %s, %s, %s)"
        # Note the 'self.' prefix here
        return self.input_error_handler(query, (user_id, user_name, email, hashed_password, user_type))

    #params=>user_id
    #this function will be called to fetch a user from the database
    #it will return the user details if the user is found
    #it will return None if the user is not found
    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        result = self.fetch_data_handler(query, (user_id,), fetch_all=False)
        return result

    #params=>field_id
    #this function will be called to fetch a specific field from the database
    #it will return the field value if the field is found
    #it will return None if the field is not found
    def get_field(self,field_id):
        query = "SELECT * FROM field WHERE field_id = %s"
        result = self.fetch_data_handler(query, (field_id), fetch_all=False)
        return result

    #params=>user_id
    #this function will be called to  fetch a specific user's field using user_id
    # it will return the field value as dictionary if the field is found
    # it will return None if the field is not found
    def get_users_field(self,user_id):
        query = """ 
                select f.field_id as field_id,user_id,field_name,field_latitude,field_longitude,field_elevation,tea_variety,plant_age_in_years
                from field as f inner join ownership as own on f.field_id = own.field_id
                where f.field_id = %s;
            """
        result=self.fetch_data_handler(query, (user_id,), fetch_all=True)
        return result

    #params=>user_id,field_id,field_name,field_latitude,field_longitude,field_elevation,tea_variety,plant_age_in_years
    #this function will be called to add a new field to the database
    #it will return True if the field is added successfully
    #it will return False if the field is not added successfully
    def add_field(self,user_id,field_id,field_name,field_latitude,field_longitude,field_elevation,tea_variety,plant_age_in_years):
        query = 'select user_id from users where user_id = %s;'
        result = self.fetch_data_handler(query, (user_id,), fetch_all=False)
        if result:
            query = 'insert into field values (%s,%s,%s,%s,%s,%s,%s);'
            result = self.input_error_handler(query,(field_id, field_name, field_latitude, field_longitude, field_elevation,tea_variety, plant_age_in_years))
            if result:
                query = 'insert into ownership values (%s,%s);'
                result = self.input_error_handler(query, (user_id, field_id))
                return result
            return "Error /n Could not add field"
        return f"This is no such an user"

    #params=>field_id
    #this function will be called to delete a field from the database
    #it will return True if the field is deleted successfully
    #it will return False if the field is not deleted successfully
    def delete_field(self,field_id):
        query = 'delete from field where field_id = %s'

    def update_field(self,field_id,field_name,field_latitude,field_longitude,field_elevation):
        query=("""
               update field 
               set field_name = %s, field_latitude = %s, field_longitude = %s, field_elevation = %s,plant_age_in_years = %s 
               where field_id = %s;
               """)
        result=self.input_error_handler(query, (field_name, field_latitude, field_longitude, field_elevation, field_id))

    #params=>scan_id
    #this function will be called to fetch a scan chat history from the database
    #it will return the scan chat history as a dictionary if the scan chat history is found
    #it will return None if the scan chat history is not found
    def get_scan_chat_history_by_scan_id(self,scan_id):
        query = 'select scan_id,chat_created_timestamp,latitude,longitude,elevation from scan_history_chat where scan_id = %s;'
        result = self.fetch_data_handler(query, (scan_id,), fetch_all=False)
        return result

    #params=>user_id
    #this function will be called to fetch a scan chat history by user id from the database
    #it will return the scan chat history as a dictionary if the scan chat history is found
    #it will return None if the scan chat history is not found
    def get_scan_chat_history_by_user_id(self,user_id):
        query="""
                select shc.scan_id as scan_id,chat_created_timestamp,longitude,latitude,elevation
                from scan_history_chat as shc inner join user_scan_history as usc on shc.scan_id = usc.scan_id
                where user_id=%s;
        """
        result = self.fetch_data_handler(query, (user_id,), fetch_all=True)
        return result

    #params=>user_id
    #this function will be called to fetch a user chat history by user id from the database
    #it will return the user chat history as a dictionary if the user chat history is found
    #it will return None if the user chat history is not found
    def get_user_chat_history_by_user_id(self,user_id):
        query="""
                select disease_name,confidence_score,generated_advice as treatment,longitude,detection_code,image_name,chat_created_timestamp as date
                from user_scan_history as ush inner join scan_history_chat as shc on ush.scan_id=shc.scan_id
                    inner join detection as d on shc.scan_id= d.scan_id
                    inner join disease as dis on d.disease_id=dis.disease_id
                    inner join applied_treatment as at on d.detection_id=at.detection_id
                    inner join treatment_recommendation as tr on at.recommendation_id = tr.recommendation_id
                where user_id=%s;
        """
        result = self.fetch_data_handler(query, (user_id,), fetch_all=True)
        return result






if __name__ == "__main__":
    db = Database()

    result=db.get_user_chat_history_by_user_id('1')
    for item in result:
        for i in item:
            print(f"{i}: {item[i]}")
        print()




















    #print(db.add_field(1,5, 'Estate Block B', 6.96000000, 6.96000000, 6.96000000, 'unknow', 30))

