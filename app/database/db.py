from datetime import datetime

import psycopg2
from psycopg2.extras import Json
from config import Config
import json


class Database:
    def __init__(self, host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASSWORD, port=Config.DB_PORT):
        self.conn = self.create_db_connection_credentials(host, database, user, password, port)
        self.cur  = self.conn.cursor()

    #-----------------------------------------------------------------------------
    # database connection operations
    #-----------------------------------------------------------------------------

    # params => host, database, user, password, port
    # this function creates a database connection
    # returns database connection object
    def create_db_connection_credentials(self, host, database, user, password, port):
        conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
        print(f"Successfully connected to the PostgreSQL database: {database}")
        return conn

    def test_db_connection(self):
        try:
            self.cur.execute('SELECT version();')
            db_version = self.cur.fetchone()
            return f"Successfully connected! PostgreSQL version: {db_version}"
        except Exception as e:
            return f"Database connection failed: {e}"

    #-----------------------------------------------------------------------------
    # Database setup operations
    #-----------------------------------------------------------------------------

    # params => file_path
    # this function runs an entire SQL script file (used to create tables)
    # returns True on success, False on failure
    def create_tables(self, file_path):
        with open(file_path, 'r') as f:
            sql_script = f.read()
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql_script)
            self.conn.commit()
            print("Tables created successfully!")
        except Exception as e:
            self.conn.rollback()
            print(f"An error occurred: {e}")
        finally:
            cursor.close()

    #-----------------------------------------------------------------------------
    # Database test operations
    #-----------------------------------------------------------------------------

    # params => file_path
    # this function runs an entire SQL script file (used to insert dummy/test data)
    # returns True on success, False on failure
    def add_dummy_data(self, file_path):
        with open(file_path, 'r') as f:
            sql_script = f.read()
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql_script)
            self.conn.commit()
            print("Dummy data added successfully!")
        except Exception as e:
            self.conn.rollback()
            print(f"An error occurred: {e}")
        finally:
            cursor.close()

    #-----------------------------------------------------------------------------
    # Database query handlers
    #-----------------------------------------------------------------------------

    # params => query, params
    # this function handles INSERT / UPDATE / DELETE — returns True on success, False on failure
    # returns True on success, False on failure
    def input_error_handler(self, query, params):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            print("Success: Database operation completed.")
            return True
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            print(f"Integrity error: {e}")
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"Unexpected error: {e}")
            return False
        finally:
            self.cur.close()
            self.cur = self.conn.cursor()


    # params => query, params, fetch_all
    # this function handles SELECT — returns dict or list of dicts, None on failure
    # returns dict or list of dicts, None on failure
    def fetch_data_handler(self, query, params=None, fetch_all=True):
        try:
            self.cur.execute(query, params or ())
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
            if hasattr(self, 'conn') and self.conn:
                self.conn.rollback()
            return None

    #-----------------------------------------------------------------------------
    # Database generator operations
    #-----------------------------------------------------------------------------

    # params=> None
    # this function returns next user_code string e.g. "USR0000001"
    # returns user_code string
    def get_new_user_code(self):
        query   = "SELECT COALESCE(MAX(user_id), 0) + 1 AS next_id FROM users"
        result  = self.fetch_data_handler(query, fetch_all=False)
        next_id = result["next_id"] if result and result["next_id"] else 1
        return f"USR{str(next_id).zfill(7)}"

    # params=> None
    # this function returns next recommendation_id and recommendation_code
    # returns recommendation_id and recommendation_code)
    def get_new_recommendation_code(self):
        query   = "SELECT COALESCE(MAX(recommendation_id), 0) + 1 AS next_id FROM treatment_recommendation"
        result  = self.fetch_data_handler(query, fetch_all=False)
        next_id = result["next_id"] if result and result["next_id"] else 1
        return next_id, f"R{str(next_id).zfill(9)}"

    # params=> None
    # this function returns next detection_id and detection_code
    # returns detection_id and detection_code
    def get_new_detection_code(self):
        query   = "SELECT COALESCE(MAX(detection_id), 0) + 1 AS next_id FROM detection"
        result  = self.fetch_data_handler(query, fetch_all=False)
        next_id = result["next_id"] if result and result["next_id"] else 1
        return next_id, f"D{str(next_id).zfill(19)}"

    #-----------------------------------------------------------------------------
    # Database user operations
    #-----------------------------------------------------------------------------

    # params=> user_code, user_name, email, password (pre-hashed bcrypt), user_type
    # this function inserts a new user — password must already be bcrypt hashed before calling this
    # returns True on success, False on failure
    def add_user(self, user_code, user_name, email, password, user_type):
        query = "INSERT INTO users (user_code, user_name, email, password, user_type) VALUES (%s, %s, %s, %s, %s)"
        return self.input_error_handler(query, (user_code, user_name, email, password, user_type))

    # params=> user_id
    # this function returns full user row as dict, or None
    # returns full user row as dict, or None
    def get_user_by_user_id(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        return self.fetch_data_handler(query, (user_id,), fetch_all=False)

    # params=> email
    # this function returns user dict (with password hash) for login validation
    # returns user dict (with password hash) for login validation
    def get_use_data_by_email(self, email):
        query = "SELECT user_id, user_code, user_name, email, password, user_type FROM users WHERE email = %s"
        return self.fetch_data_handler(query, (email,), fetch_all=False)

    # params => email
    # this function returns user dict if email exists, None otherwise — used for duplicate check on signup
    # returns user dict if email exists, None otherwise
    def check_email_exists(self, email):
        query = "SELECT user_id FROM users WHERE email = %s"
        return self.fetch_data_handler(query, (email,), fetch_all=False)


    # user refresh tokens table operations

    # params => user_id, token_hash, device_info, latitude, longitude, expires_at
    # this function stores a new hashed refresh token for session management
    # returns True on success, False on failure
    def create_new_session_token(self, user_id, token_hash, device_info, latitude, longitude, expires_at):
        query = """
            INSERT INTO user_refresh_token(user_id, token_hash, device_info, latitude, longitude, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.input_error_handler(query, (user_id, token_hash, device_info, latitude, longitude, expires_at))

    # params => token_hash
    # this function marks a refresh token as revoked on logout
    # returns True on success, False on failure
    def revoked_session_token(self, token_hash):
        query = "UPDATE user_refresh_token SET is_revoked = TRUE WHERE token_hash = %s"
        return self.input_error_handler(query, (token_hash,))

    #-----------------------------------------------------------------------------
    # fields table operations
    #-----------------------------------------------------------------------------

    # params => user_id, field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years
    # this function inserts a new field — field_id is auto-generated by SERIAL
    # returns True on success, False on failure
    def add_field(self, user_id, field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years):
        query = """
            INSERT INTO field(user_id, field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.input_error_handler(query, (user_id, field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years))

    # params => field_id
    # this function returns a single field row as dict
    # returns field row as dict, or None on failure
    def get_field(self, field_id):
        query = "SELECT * FROM field WHERE field_id = %s"
        return self.fetch_data_handler(query, (field_id,), fetch_all=False)

    # params => user_id
    # this function returns all fields belonging to a user as list of dicts
    # returns list of field rows as dicts, or empty list on failure
    def get_users_field_by_user_id(self, user_id):
        query = "SELECT * FROM field WHERE user_id = %s ORDER BY field_name ASC"
        return self.fetch_data_handler(query, (user_id,), fetch_all=True)

    # params => user_id
    # this function returns only field_id and field_name
    # returns list of field rows as dicts, or empty list on failure
    def get_field_names_by_user_id(self, user_id):
        query = "SELECT field_id, field_name FROM field WHERE user_id = %s ORDER BY field_name ASC"
        return self.fetch_data_handler(query, (user_id,), fetch_all=True)

    # params => field_id
    # this function deletes a field
    # returns True on success, False on failure
    def delete_field_by_field_id(self, field_id):
        query = "DELETE FROM field WHERE field_id = %s"
        return self.input_error_handler(query, (field_id,))

    # params => field_id, field_name, field_latitude, field_longitude,field_elevation, tea_variety, plant_age_in_years
    # this function updates all editable columns on a field row
    # returns True on success, False on failure
    def update_field(self, field_id, field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years):
        query = """
            UPDATE field
            SET field_name = %s, field_latitude = %s, field_longitude = %s,
                field_elevation = %s, tea_variety = %s, plant_age_in_years = %s
            WHERE field_id = %s
        """
        return self.input_error_handler(query, (field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years, field_id))


    #-----------------------------------------------------------------------------
    # scan history chat table operations
    #-----------------------------------------------------------------------------

    # params => chat_code, timestamp, latitude, longitude, elevation
    # this function inserts a new scan session — scan_id is auto-generated by SERIAL
    # returns True on success, False on failure
    def add_scan_history_chat(self, chat_code, timestamp, latitude, longitude, elevation):
        query = """
            INSERT INTO scan_history_chat(chat_code, chat_created_timestamp, latitude, longitude, elevation)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.input_error_handler(query, (chat_code, timestamp, latitude, longitude, elevation))

    # params => scan_id
    # this function used to get a single scan chat history row by scan_id
    # returns scan chat history row as dict, or None on failure
    def get_scan_chat_history_by_scan_id(self, scan_id):
        query = "SELECT scan_id, chat_code, chat_created_timestamp, latitude, longitude, elevation FROM scan_history_chat WHERE scan_id = %s"
        return self.fetch_data_handler(query, (scan_id,), fetch_all=False)

    # params => chat_code
    # this function used to get a single scan chat history row by chat_code
    # returns scan chat history row as dict, or None on failure
    def get_scan_chat_history_by_chat_code(self, chat_code):
        query = "SELECT scan_id, chat_code, chat_created_timestamp, latitude, longitude, elevation FROM scan_history_chat WHERE chat_code = %s"
        return self.fetch_data_handler(query, (chat_code,), fetch_all=False)

    # params => user_id
    # this function returns all scan chat history for a user
    # returns list of scan chat history rows as dicts, or empty list on failure
    def get_scan_chat_history_by_user_id(self, user_id):
        query = """
            SELECT shc.scan_id, chat_created_timestamp, chat_code, longitude, latitude, elevation
            FROM scan_history_chat AS shc
            INNER JOIN user_scan_history AS usc ON shc.scan_id = usc.scan_id
            WHERE usc.user_id = %s
            ORDER BY chat_created_timestamp DESC
        """
        return self.fetch_data_handler(query, (user_id,), fetch_all=True)

    # params => chat_code
    # this function used to remove a scan chat history by chat_code
    # returns True on success, False on failure
    def remove_scan_history_chat_by_chat_code(self, chat_code):
        query = "DELETE FROM scan_history_chat WHERE chat_code = %s"
        return self.input_error_handler(query, (chat_code,))

    def get_chat_codes(self):
        query = "select chat_code from scan_history_chat order by chat_code ;"
        return self.fetch_data_handler(query)

    #-----------------------------------------------------------------------------
    # user scan history table operations
    #-----------------------------------------------------------------------------

    # params => user_id, field_id, scan_id
    # this function used to link user + field + scan together in the junction table
    # returns True on success, False on failure
    def add_user_scan_history(self, user_id, field_id, scan_id):
        query = "INSERT INTO user_scan_history(user_id, field_id, scan_id) VALUES (%s, %s, %s)"
        return self.input_error_handler(query, (user_id, field_id, scan_id))

    # params => user_id
    # this function used to get full scan_chat_history for a user
    # returns list of chat history rows as dicts, or empty list on failure
    def get_user_chat_history_by_user_id(self, user_id):
        query = """
            SELECT
                dis.disease_name,
                d.confidence_score,
                tr.generated_advice        AS treatment,
                field_name                 as field_name,
                shc.longitude              AS longitude,
                chat_code                  as barcode,
                d.image_name               AS imageDataUrl,
                shc.chat_created_timestamp AS date,
                severity_level,
                recovery_percentage        as recovery_percentage,
                status                     as detection_status
            FROM field as f
                INNER JOIN user_scan_history      AS ush on f.field_id = ush.field_id
                INNER JOIN scan_history_chat      AS shc ON ush.scan_id          = shc.scan_id
                INNER JOIN detection              AS d   ON shc.scan_id          = d.scan_id
                INNER JOIN disease                AS dis ON d.disease_id         = dis.disease_id
                INNER JOIN applied_treatment      AS at  ON d.detection_id       = at.detection_id
                INNER JOIN treatment_recommendation AS tr ON at.recommendation_id = tr.recommendation_id
            WHERE ush.user_id = %s
            ORDER BY shc.chat_created_timestamp DESC
        """
        return self.fetch_data_handler(query, (user_id,), fetch_all=True)

    #-----------------------------------------------------------------------------
    # disease table operations
    #-----------------------------------------------------------------------------

    # params => disease_name
    # this function used to get disease_id by disease_name
    # returns disease_id integer, or None if not found
    def get_disease_id_by_disease_name(self, disease_name):
        query  = "SELECT disease_id FROM disease WHERE disease_name = %s"
        result = self.fetch_data_handler(query, (disease_name,), fetch_all=False)
        return result['disease_id'] if result else None



    # treatment recommendation table operations

    # params => recommendation_id, recommendation_code, generated_advice,
    #           RAG_confidence_score (0-100), model_version
    # Inserts a new AI-generated treatment recommendation
    def add_recommended_treatment(self, recommendation_id, recommendation_code, generated_advice, RAG_confidence_score, model_version=Config.MODEL_VERSION):
        query = """
            INSERT INTO treatment_recommendation(recommendation_id, recommendation_code, generated_advice, RAG_confidence_score, model_version)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.input_error_handler(query, (recommendation_id, recommendation_code, generated_advice, RAG_confidence_score, model_version))



    # detection table operations

    # params => detection_id, detection_code (20 chars), scan_id, disease_id,
    #           confidence_score (0-100), bounding_box (dict or JSON string),
    #           severity_level (low/medium/high), lesion_count,
    #           healthy_leaf_area (0-100), affected_area (0-100),
    #           image_name, recovery_percentage (0-100), status
    # Validates all inputs then inserts a detection record
    def add_detection(self, detection_id:int, detection_code:str, scan_id:int, disease_id:int, confidence_score:float,
                      bounding_box:dict, severity_level:str, lesion_count:int, healthy_leaf_area:float,
                      affected_area:float, image_name:str,recovery_percentage=0.00, status='new'):

        detection_id   = int(detection_id)
        detection_code = str(detection_code)
        if len(detection_code) != 20:
            return {'error': 'detection_code must be exactly 20 characters'}

        scan_id    = int(scan_id)
        disease_id = int(disease_id)

        confidence_score = round(float(confidence_score), 2)
        if not (0 <= confidence_score <= 100):
            return {'error': 'confidence_score must be between 0 and 100'}

        bounding_box = Json(json.loads(bounding_box)) if isinstance(bounding_box, str) else Json(bounding_box)

        severity_level = str(severity_level).lower()
        if severity_level not in ('low', 'medium', 'high'):
            return {'error': 'severity_level must be one of: low, medium, high'}

        lesion_count      = int(lesion_count)

        healthy_leaf_area = round(float(healthy_leaf_area), 2)
        if not (0 <= healthy_leaf_area):
            return {'error': 'healthy_leaf_area must be greater than 0'}

        affected_area = round(float(affected_area), 2)
        if not (0 <= affected_area):
            return {'error': 'affected_area must be between greater than 0'}

        image_name = str(image_name)
        recovery_percentage = round(float(recovery_percentage), 2)
        if not (0 <= recovery_percentage <= 100):
            return {'error': 'recovery_percentage must be between 0 and 100'}

        status = str(status)
        if status not in ('new','good_recovery','moderate_recovery','poor_recovery','escalated'):
            return {'error': 'status must be one of: new, under_treatment, recovered, escalated'}

        query = """
            INSERT INTO detection(
                detection_id, detection_code, scan_id, disease_id, confidence_score,
                bounding_box, severity_level, lesion_count, healthy_leaf_area,
                affected_area, image_name, recovery_percentage, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.input_error_handler(query, (
            detection_id, detection_code, scan_id, disease_id, confidence_score,
            bounding_box, severity_level, lesion_count, healthy_leaf_area,
            affected_area, image_name, recovery_percentage, status
        ))

    # params => detection_id
    # Deletes a detection record — cascades to applied_treatment
    def remove_detection_by_detection_id(self, detection_id):
        query = "DELETE FROM detection WHERE detection_id = %s"
        return self.input_error_handler(query, (detection_id,))

    def detection_data_by_chat_code(self, chat_code):
        query = """
                select *
                from scan_history_chat as shc inner join detection as d on shc.scan_id = d.scan_id
                where chat_code= %s
                order by shc.chat_created_timestamp desc
                LIMIT 1;
        """
        return self.fetch_data_handler(query, (chat_code,))


    # applied treatment table operations

    # params => detection_id, recommendation_id
    # Links a detection to its treatment recommendation
    def add_applied_treatment(self, detection_id, recommendation_id):
        query = "INSERT INTO applied_treatment(detection_id, recommendation_id) VALUES (%s, %s)"
        return self.input_error_handler(query, (detection_id, recommendation_id))

    def remove_applied_treatment(self,detection_id):
        query = "DELETE FROM applied_treatment WHERE detection_id = %s"
        return self.input_error_handler(query, (detection_id,))