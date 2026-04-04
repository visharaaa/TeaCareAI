import json
from flask import url_for
import os
from datetime import datetime, timezone,timedelta
import threading
import queue
import bcrypt
import requests

from app.database.db import Database
from app.services.leaf_verifier import LeafVerifier
from app.services.tea_disease_identifier import TeaDiseaseIdentifier
from app.services.treatment_recommendations import TeaDiseaseRAG
from app.services.recovery_tracker import TreatmentProgressTracker
from config import Config

# create a Database instance
db = Database()

# Create a threading lock to ensure that only one thread can access the model at a time
threading_lock= threading.Lock()

# Create separate queues for each model to handle the tasks
vision_queue = queue.Queue()
rag_queue = queue.Queue()
NN_queue = queue.Queue()

# Create a lock for database operations
code_lock = threading.Lock()

## params => None
# This function will run in a separate thread and continuously process images from the vision_queue
def tea_disease_identifier_worker():
    print("Background LeafVerifier worker starting...")
    leaf_verifier= LeafVerifier(
        model=Config.CLIP_MODEL,
        positive_labels=Config.CLIP_POSITIVE_LABELS,
        negative_labels=Config.CLIP_NEGATIVE_LABELS,
        threshold=Config.CLIP_THRESHOLD,
        imgPath=Config.UPLOAD_FOLDER
    )
    print("Background TeaDiseaseIdentifier worker starting...")
    # Load the model into new object
    tea_disease_identifier=TeaDiseaseIdentifier(Config.TEA_DISEASE_IDENTIFIER_MODEL_PATH,Config.UPLOAD_FOLDER)
    print("TeaDiseaseIdentifier Model loaded successfully! Worker is ready.")
    while True:
        #get the next image  from the queue
        file_name,response_queue=vision_queue.get()
        # Wait for the tread to be completely free
        with threading_lock:
            try:
                # Check the images contain a leafs
                leaf_verifier_result=leaf_verifier.is_tea_leaf(file_name)
                print(leaf_verifier_result)
                if leaf_verifier_result == False:
                    raise Exception(f"The uploaded image does not appear to be a tea leaf. Please upload a clear image of a tea leaf for accurate diagnosis.")

                # Process the one image.
                result=tea_disease_identifier.get_disease(file_name)
                # Put the result into this specific user's private pager
                response_queue.put(result)
            except Exception as e:
                # If the model crashes on a bad image, send the error back
                print(e)
                response_queue.put(Exception(f"Error processing image: {str(e)}"))
        # Tell the main waiting room this task is officially done
        vision_queue.task_done()

# params => None
# This function will run in a separate thread and continuously process the RAG input from the rag_queue
def tea_disease_rag_worker():
    print("Background TeaDiseaseRAG worker starting...")
    # Load the model into new object
    tea_disease_rag=TeaDiseaseRAG(excel_path=Config.KB_PATH,db_path=Config.VECTOR_DB_PATH,embedding_model = Config.EMBEDDING_MODEL)
    print("TeaDiseaseRAG Model loaded successfully! Worker is ready.")
    while True:
        # get the next disease from the queue
        inputs,response=rag_queue.get()
        disease_name, severity_level = inputs
        with threading_lock:
            try:
                #getting the recommendations
                llm_response,confidence=tea_disease_rag.get_treatment(disease_name, severity_level)
                result=(llm_response,confidence)
                response.put(result)
            except Exception as e:
                # If the model crashes, send the error back
                response.put(Exception(str(e)))
        rag_queue.task_done()

# This function will run in a separate thread and continuously process the input from the NN_queue
def recovery_tracker_worker():
    print("Background RecoveryTracker worker starting...")
    # Load the model into new object
    treatment_progress_tracker=TreatmentProgressTracker(
        model_path=Config.NN_MODEL_PATH,
        scaler_path=Config.NN_SCALER_PATH,
        feature_cols_path=Config.NN_FEATURE_COLUMNS_PATH
    )
    print("LeafEvaluator Model loaded successfully! Worker is ready.")
    while True:
        try:
            inputs,response=NN_queue.get()
            prediction=treatment_progress_tracker.check_progress(
                disease=inputs['disease'],
                days_after_treatment=inputs['days_after_treatment'],
                initial_affected_area_pct=inputs['initial_affected_area_pct'],
                affected_area_pct=inputs['affected_area_pct'],
                color_deviation=inputs['color_deviation'],
                humidity=inputs['humidity'])
            response.put(prediction)
        except Exception as e:
            # If the model crashes on a bad image, send the error back
            response.put(Exception(f"Error processing image: {str(e)}"))
        finally:
            NN_queue.task_done()

# params => user_id, img, field_id, chat_code, latitude, longitude, elevation
# This is the main function that the Flask route will call when it needs a prediction. 
# It starts the background workers and processes the image through the queues.
# returns error message if any step fails, otherwise returns the prediction result
def predict(user_code,img,field_id, chat_code:str,latitude, longitude,elevation=None):
    user_id=db.get_user_id_by_user_code(user_code)
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{img.filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    img.save(file_path)

    # Create a private pager
    response_vision_queue = queue.Queue()
    response_rag_queue=queue.Queue()
    response_NN_queue=queue.Queue()

    # Put the filename and the private pager into the task_queue
    vision_queue.put((filename, response_vision_queue))
    # The Flask route pauses right here and waits for the worker to finish the math
    vision_result = response_vision_queue.get()

    # check: Did the worker return an error?
    if isinstance(vision_result, Exception):
        print(f"Prediction failed: {vision_result}")
        error = f"Failed to process Image : {vision_result}"
        result = {
            'status': "error",
            'error': error
        }
        return result

    # prediction from disease identifier
    disease_name=vision_result["disease_name"]
    disease_identifier_confidence_score=vision_result['confident']
    infection_percentage=vision_result["infection_percentage"]
    severity_level=vision_result["severity_level"]
    healthy_leaf_area=vision_result["healthy_leaf_area"]
    affected_area=vision_result["affected_area"]
    lesion_count=vision_result["lesion_count"]
    masks=vision_result['masks'],
    color_deviation=vision_result['color_deviation']

    already_has = False
    recovery_percentage = 0
    recovery_status = 'new'

    skip,standardized_disease_name=standardize_disease_name(disease_name)

    # input for recovery_tracker
    rag_input=(standardize_disease_name_for_RAG(disease_name),severity_level)
    rag_queue.put((rag_input, response_rag_queue))


    if not skip:
        # get the detection history data using chat_code
        detection_history=db.detection_data_by_chat_code(chat_code)


        # detection_history empty mean this is a new chat
        if detection_history != []:
            already_has=True
            detection_history=detection_history[0]

        # this chat already has mean this is the second time of detection, which means the user has applied the treatment and want to check the recovery status
        if already_has:

            # if location data is empty getting the location data from database by chat_code in scan_history_chat table
            if latitude == '' or longitude == '':
                result = db.get_location_by_chat_code(
                    chat_code)  # to avoid the result= None error when the chat_code is not exist in the database
                if result != None:
                    if None not in result.values():  # to avoid the location data be None which will cause the error when convert to float
                        latitude = str(result['latitude'])
                        longitude = str(result['longitude'])

            # if location data is empty getting the location data from database by field in field table
            if latitude == '' or longitude == '':
                result = db.get_field_location_by_field_id(field_id)
                latitude = str(result['latitude'])
                longitude = str(result['longitude'])

            #get whether data like humidity and temperature
            whether_data=get_weather_data(latitude,longitude)

            # input for NN
            NN_input = {
                'disease': disease_name,
                'days_after_treatment': (datetime.now(timezone.utc) - detection_history['detected_at']).days,
                'initial_affected_area_pct':float( (detection_history["affected_area"]/detection_history["healthy_leaf_area"])*100),
                'affected_area_pct': infection_percentage,
                'color_deviation': color_deviation,
                'humidity': whether_data["humidity"],
            }
            NN_queue.put((NN_input, response_NN_queue))

            # prediction from disease identifier
            NN_result = response_NN_queue.get()

            if isinstance(NN_result, Exception):
                print(f"Prediction failed: {NN_result}")
                error='Failed to process Neural Network'
                result = {
                    'status': "error",
                    'error': error
                }
                return result

            recovery_percentage = round(NN_result["change"], 2)
            recovery_status = NN_result["status"]


    # prediction from disease identifier
    rag_result = response_rag_queue.get()

    if isinstance(rag_result, Exception):
        print(f"Prediction failed: {rag_result}")
        error = 'Failed to process RAG'
        result = {
            'status': "error",
            'error': error
        }
        return result

    llm_response, RAG_confidence_score=rag_result


    #save to database
    try:
        save_data(
              user_id=user_id,
              field_id=field_id,
              chat_code=chat_code,
              latitude=latitude,
              longitude=longitude,
              elevation=elevation,
              disease_name=standardized_disease_name,
              disease_identifier_confidence_score=float(disease_identifier_confidence_score),
              bounding_box=json.dumps(masks),
              severity_level=str(severity_level).lower(),
              lesion_count=int(lesion_count),
              healthy_leaf_area=int(healthy_leaf_area),
              affected_area=int(affected_area),
              image_name=str(filename),
              RAG_confidence_score=float(RAG_confidence_score) ,
              generated_advice=llm_response,
              status=recovery_status,
              recovery_percentage=float(recovery_percentage),
              skip=skip
              )
        
    except Exception as e:
        print(f"Warning: could not save to DB: {e}")

    result = {
        'status':     standardized_disease_name,
        'confidence': str(disease_identifier_confidence_score) + '%',
        'treatment':  llm_response,
        'severity_level': severity_level,
        'recovery_percentage': str(recovery_percentage),
        'recovery_state': recovery_status,
        'detection_status': format_recovery_status(recovery_status),
        'barcode': chat_code,
        'location': f"{latitude},{longitude}"
    }

    return result

# params => user_name, email, password, user_type
# This function will be called by the Flask route when a user tries to register a new account. 
# It checks if the email is already in use, hashes the password, and then saves the new user to the database.
# returns a tuple of (success: bool, message: str or None)
def register_user(user_name, email, password, user_type):
    
    #checking if the user already exists
    existing = db.check_email_exists(email)
    if existing:
        return False, "An account with this email already exists."

    #get new user_code
    user_code = db.get_new_user_code()

    # Hash password with bcrypt
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    #inserting the user into the database
    result =db.add_user(user_code, user_name, email, hashed, user_type)

    return (True, None) if result else (False, "Could not create account. Please try again.")

# params => user_id
# This function will be called to load the user's chat history
# It checks if the email exists, verifies the password
# returns the user_id if successful
def load_user_chat(user_code):
    user_id=db.get_user_id_by_user_code(user_code)
    print(user_id)
    records = db.get_user_chat_history_by_user_id(user_id)
    data = []
    for record in records:
        image_filename = record.get('imagedataurl') or ''
        image_url = None
        if image_filename:
            full_path = os.path.join('static', 'uploaded_leaves', image_filename)
            if os.path.exists(full_path):  # only include if file actually exists on disk
                image_url = url_for('static', filename='uploaded_leaves/' + image_filename)
        data.append({
            'disease_name': record.get('disease_name', 'Unknown'),
            'confidence':   str(record.get('confidence_score'))+ '%',
            'treatment':    record.get('treatment', ''),
            'field_name': record.get('field_name', ''),
            'location':     record.get('longitude', '—'),
            'barcode':      record.get('barcode', '—'),
            'imageDataUrl': image_url,
            'date':         record.get('date', '—'),
            'severity_level': record.get('severity_level', ''),
            'recovery_percentage': record.get('recovery_percentage', 0),
            'detection_status':record.get('detection_status'),
        })
    #print(data)
    return data

def load_chat_code_drop_down(user_code):
    user_id=db.get_user_id_by_user_code(user_code)
    result=db.get_user_chat_code_by_user_id(user_id)
    return result

# params => none
# This function will return the secret key for Flask session management from the config file
def get_secret_key():
    return Config.SECRET_KEY

# params => none
# This function will return the session lifetime for Flask session management from the config file
def get_session_lifetime():
    return timedelta(hours=Config.SESSION_LIFETIME)

# params => user_id, field_name,field_latitude, field_longitude,field_elevation, tea_variety, plant_age
# This function will be called when the user adds a new field. 
# It saves the field information to the database.
def add_field_to_db(user_code, field_name,field_latitude, field_longitude,field_elevation, tea_variety, plant_age):
    # get user_id using user_id
    user_id = db.get_user_id_by_user_code(user_code)

    # add field to the database
    result = db.add_field(
        user_id=user_id,
        field_name=field_name,
        field_latitude=field_latitude,
        field_longitude=field_longitude,
        field_elevation=field_elevation,
        tea_variety=tea_variety,
        plant_age_in_years=plant_age
    )
    return result

# params => user_id
# This function will be called to get the field details for a specific user.
# returns a list of fields associated with the user_id
def get_users_field_details(user_code):
    user_id = db.get_user_id_by_user_code(user_code)
    # Get the field details for the user from the database
    result=db.get_field_names_by_user_id(user_id)
    return result

# params => disease_name
# This function will use to standardize the disease name to make sure the disease name in database is consistent, 
# which will avoid the error when query the disease_id by disease_name in database
# return the standardized disease name
def standardize_disease_name(disease_name):
    match disease_name:
        case 'blister_blight':
            return False,'Blister Blight'
        case 'brown_blight':
            return False,'Brown Blight'
        case 'grey_blight':
            return False,'Grey Blight'
        case 'helopeltis':
            return False,'Helopeltis'
        case 'red_rust':
            return False,'Red Rust'
        case 'leaf':
            return False,'Healthy Leaf'
        case _:
            return True,"Unknown Disease"

def standardize_disease_name_for_RAG(disease_name):
    match disease_name:
        case 'blister_blight':
            return 'Blister Blight'
        case 'brown_blight':
            return 'Brown Blight'
        case 'grey_blight':
            return 'Grey Blight'
        case 'helopeltis':
            return False, 'Red Spider'
        case 'red_rust':
            return False, 'Red Rust'
        case 'leaf':
            return False, 'Healthy Leaf'
        case _:
            return True, "no disease"

# params => user_id, field_id, chat_code, latitude, longitude, elevation, disease_name, disease_identifier_confidence_score, bounding_box, severity_level, lesion_count, healthy_leaf_area, affected_area, image_name, RAG_confidence_score, generated_advice, recovery_percentage, status
# This function will be called to save the detection and treatment data to the database after each detection.
# returns a tuple of (success: bool, message: str)
#scan_id and chat code are the same
def save_data(user_id:int,field_id:int,chat_code:str,latitude:float,longitude:float,elevation:float,disease_name:str,disease_identifier_confidence_score:float,bounding_box:json,severity_level:str,lesion_count:int,
              healthy_leaf_area:float,affected_area:float,image_name:str,RAG_confidence_score:float,generated_advice:str,skip:bool,recovery_percentage=0.00,status='new'):

    # Check if the chat_code already exists
    result=db.get_scan_chat_history_by_chat_code(chat_code)

    # initialize the variables
    added=False
    already_there=False
    detection_id=None
    user_scan_result = None
    disease_id = None
    detection_result = None
    recommendation_result = None
    applied_treatment_result = None

    # result is not None means this chat_code already exists in the database, which means this is not the first time to detect for this chat, 
    # just need to add the new detection data to the detection table and link it with the scan_history_chat table
    if result:
        # If it exists, extract the integer scan_id
        scan_id = result.get('scan_id')
        already_there=True
    else:
        creation_result = None
        try:
            # create a new chat
            creation_result=db.add_scan_history_chat(
                chat_code=chat_code,
                timestamp=datetime.now(),
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )
            print("New scan created")
            added=True
        except Exception as e:
            print(e)
        finally:
            if not creation_result:
                return False,'Error when creating new scan history.'

        # get chat_code and scan_id
        new_record = db.get_scan_chat_history_by_chat_code(chat_code)
        if new_record:
            scan_id = new_record.get('scan_id')
        else:
            return False, 'Error retrieving new scan ID.'

    # if not already_there means this is a new chat, need to add the relationship between user, field and scan history in the user_scan_history table
    if not already_there:
        try:
            #add the values to user_scan_history which table create relationship between user,field and scan_history_chat tables
            user_scan_result=db.add_user_scan_history(user_id, field_id, scan_id)
        except Exception as e:
            print(f" error : {e}")
        finally:
            if (not user_scan_result) and added:
                # delete the row which is last added
                db.remove_scan_history_chat_by_chat_code(chat_code)
                return False,'Error when linking user to scan history.'


    try:
        # get the disease_id for the disease_name
        disease_id=db.get_disease_id_by_disease_name(disease_name)
    except Exception as e:
        print(e)
    finally:
        if not disease_id:
            if added:
                db.remove_scan_history_chat_by_chat_code(chat_code)
            return False,'Disease mismatch.'

    try:

        #get new detection_id and detection_code
        detection_id,detection_code=db.get_new_detection_code()

        # store the output from disease_identifier and recovery traker into detection table in database
        detection_result = db.add_detection(
            detection_id=detection_id,
            detection_code=detection_code,
            scan_id=scan_id,
            disease_id=disease_id,
            confidence_score=disease_identifier_confidence_score,
            bounding_box=bounding_box,
            severity_level=severity_level,
            lesion_count=lesion_count,
            healthy_leaf_area=healthy_leaf_area,
            affected_area=affected_area,
            image_name=image_name,
            recovery_percentage=recovery_percentage,
            status=status
        )
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if not detection_result:
            if added:
                db.remove_scan_history_chat_by_chat_code(chat_code)
            return False,'Error when adding new detection.'

    if not skip:
        try:
            # get new recommendation_id and recommendation_code
            recommendation_id,recommendation_code=db.get_new_recommendation_code()

            # save the treatment recommendation result into recommended_treatment table
            recommendation_result=db.add_recommended_treatment(
                recommendation_id=recommendation_id,
                recommendation_code=recommendation_code,
                generated_advice=generated_advice,
                RAG_confidence_score=RAG_confidence_score
            )
            # link the detection and recommendation in the applied_treatment table
            applied_treatment_result=db.add_applied_treatment(
                detection_id=detection_id,
                recommendation_id=recommendation_id
            )

        except Exception as e:
            print(e)

        finally:
            if not (recommendation_result and applied_treatment_result):
                print('Deleting recommendation...')
                db.remove_detection_by_detection_id(detection_id)
                db.remove_applied_treatment(detection_id)
                if added:
                    db.remove_scan_history_chat_by_chat_code(chat_code)
                return False,'Error when storing treatment.'

    print("added to db")
    return True,'Data added successfully.'

# params => latitude, longitude
# This function will be called to get the weather data from OpenWeatherMap API by latitude and longitude, which will be used as one of the input for recovery tracker model
# returns a dictionary with humidity and temperature
def get_weather_data(latitude,longitude):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={Config.OPENWEATHERMAP_API_KEY}")
    response=response.json()
    humidity=response['main']['humidity']
    temperature=response['main']['temp']
    temperature-=273.15
    print(temperature)
    return {'humidity':humidity, 'temperature':temperature}


def get_elevation(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lng}&key={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            elevation = data['results'][0]['elevation']
            return elevation
        else:
            print(f"API Error: {data['status']}")
            return None

    except Exception as e:
        print(f"Connection error: {e}")
        return None

# params => None
# This function is used to generate a new unique chat code for each new chat. 
# It checks the existing chat codes in the database, finds the maximum one, and generates the next one in hexadecimal format.
# returns a new unique chat code in hexadecimal format
def generate_new_chat_code():
    results=db.get_chat_codes()
    current_chat_codes=[]
    for result in results:
        current_chat_codes.append(int(result['chat_code'],16))
    if not(current_chat_codes):
        return decimal_to_hex(1)
    max_code=max(current_chat_codes)
    for i in range(1,max_code+1):
        if i not in current_chat_codes:
            return decimal_to_hex(i)
    return decimal_to_hex(max_code+1)

# params => number
# This function is used to convert a decimal number to a hexadecimal string, which will be used for generating chat codes. 
# It ensures that the hexadecimal string is always 10 characters long by padding with zeros if necessary.
# returns a hexadecimal string representation of the input number, padded to 10 characters
def decimal_to_hex(number):
    return hex(number)[2:].zfill(10)

# params => raw_recovery_status
# This function is used to format the raw recovery status returned by the NN model into a more user-friendly format for display on the frontend.
# returns a formatted string representation of the recovery status
def format_recovery_status(raw):
    map = {
        'new':           'New',
        'improving':     'Improving',
        'stable':        'Stable',
        'deteriorating': 'Deteriorating',
    }
    trimmed = (raw or '').strip().lower()
    if trimmed in map:
        return map[trimmed]
    return trimmed.replace('_', ' ').title()


#initialize the threads
tea_disease_identifier_worker_thread = threading.Thread(target=tea_disease_identifier_worker, daemon=True) ## daemon=True means this thread will automatically shut down when kill the Flask server
tea_disease_rag_worker_thread=threading.Thread(target=tea_disease_rag_worker,daemon=True)
tea_recovery_tracker_worker_thread=threading.Thread(target=recovery_tracker_worker,daemon=True)

#start the threads in background processing
tea_disease_identifier_worker_thread.start()
tea_disease_rag_worker_thread.start()
tea_recovery_tracker_worker_thread.start()