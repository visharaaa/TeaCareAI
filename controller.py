import json

from flask import url_for
import os
from datetime import datetime
import threading
import queue
import bcrypt
from datetime import timedelta
import requests


from app.database.db import Database
from app.services.tea_disease_identifier import TeaDiseaseIdentifier
from app.services.treatment_recommendations import TeaDiseaseRAG
from app.services.recovery_tracker import TreatmentProgressTracker
from config import Config


db = Database()


threading_lock= threading.Lock()
vision_queue = queue.Queue()
rag_queue = queue.Queue()
NN_queue = queue.Queue()



code_lock = threading.Lock()






def tea_disease_identifier_worker():
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
                # Process the one image.
                result=tea_disease_identifier.get_disease(file_name)

                # Put the result into this specific user's private pager
                response_queue.put(result)

            except Exception as e:
                # If the model crashes on a bad image, send the error back
                response_queue.put(Exception(f"Error processing image: {str(e)}"))

        # Tell the main waiting room this task is officially done
        vision_queue.task_done()


def tea_disease_rag_worker():
    print("Background TeaDiseaseRAG worker starting...")

    # Load the model into new object
    tea_disease_rag=TeaDiseaseRAG(excel_path=Config.KB_PATH,db_path=Config.VECTOR_DB_PATH)

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
                response.put(Exception(f"Error processing image: {str(e)}"))

        rag_queue.task_done()


def recovery_tracker_worker():
    print("Background RecoveryTracker worker starting...")
    treatment_progress_tracker=TreatmentProgressTracker(
        model_path=Config.NN_MODEL_PATH,
        scaler_path=Config.NN_SCALER_PATH,
        feature_cols_path=Config.NN_FEATURE_COLUMNS_PATH
    )
    print("LeafEvaluator Model loaded successfully! Worker is ready.")
    while True:
        try:
            inputs,response=NN_queue.get()
            prediction=treatment_progress_tracker.predict_recovery(
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


def predict(user_id,img,field_id, chat_code:str,latitude=10, longitude=20,elevation=2):
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)


    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{img.filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    img.save(file_path)

    # Create a private pager just for THIS specific web request
    response_vision_queue = queue.Queue()
    response_rag_queue=queue.Queue()
    response_NN_queue=queue.Queue()


    # Put the filename and the private pager into the task_queue
    vision_queue.put((filename, response_vision_queue))

    # The Flask route pauses right here and waits for the worker to finish the math
    vision_result = response_vision_queue.get()

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

    # check: Did the worker return an error?
    if isinstance(vision_result, Exception):
        print(f"Prediction failed: {vision_result}")
        return {'error': 'Failed to process image'}


    # input for recovery_tracker
    rag_input=(disease_name,severity_level)
    rag_queue.put((rag_input, response_rag_queue))

    detection_history=db.detection_data_by_chat_code(chat_code)
    already_has=False
    status = 'new'
    recovery_percentage=0
    if detection_history>0:
        already_has=True

    #latitude,longitude,elevation,detected_at,healthy_leaf_area,affected_area


    if already_has:

        #get whether data like humidity and temperature
        whether_data=get_weather_data(latitude,longitude)

        # input for NN
        NN_input = {
            'disease': disease_name,
            'days_after_treatment': 3,
            'initial_affected_area_pct': (detection_history["affected_area"]/detection_history["healthy_leaf_area"])*100,
            'affected_area_pct': infection_percentage,
            'color_deviation': color_deviation,
            'humidity': whether_data["humidity"],
        }

        NN_queue.put((NN_input, response_NN_queue))

        # prediction from disease identifier
        NN_result = response_NN_queue.get()

        if isinstance(NN_result, Exception):
            print(f"Prediction failed: {NN_result}")
            return {'error': 'Failed to process Neural Network'}

        recovery_percentage = NN_result[0]
        recovery_status = NN_result[1]


    # prediction from disease identifier
    rag_result = response_rag_queue.get()

    if isinstance(rag_result, Exception):
        print(f"Prediction failed: {rag_result}")
        return {'error': 'Failed to get response RAG'}


    #print(result)
    #print(f"rag_result : {rag_result}")

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
              disease_name=disease_name,
              disease_identifier_confidence_score=float(disease_identifier_confidence_score),
              bounding_box=json.dumps(masks),
              severity_level=str(severity_level).lower(),
              lesion_count=int(lesion_count),
              healthy_leaf_area=int(healthy_leaf_area),
              affected_area=int(affected_area),
              image_name=str(filename),
              RAG_confidence_score=float(RAG_confidence_score),
              generated_advice=llm_response,
              status=str(status),
              recovery_percentage=float(recovery_percentage)
                  )
    except Exception as e:
        print(f"Warning: could not save to DB: {e}")

    result = {
        'status':     standardize_disease_name(disease_name),
        'confidence': str(disease_identifier_confidence_score) + '%',
        'treatment':  llm_response,
        'severity_level': severity_level,
        'recovery_percentage': str(recovery_percentage),
        'detection_status': status,
        'barcode': chat_code,
        'location': f"{latitude},{longitude}"
    }
    return result








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

#initialize the threads
tea_disease_identifier_worker_thread = threading.Thread(target=tea_disease_identifier_worker, daemon=True) ## daemon=True means this thread will automatically shut down when kill the Flask server
tea_disease_rag_worker_thread=threading.Thread(target=tea_disease_rag_worker,daemon=True)
tea_recovery_tracker_worker_thread=threading.Thread(target=recovery_tracker_worker,daemon=True)

#start the threads in background processing
tea_disease_identifier_worker_thread.start()
tea_disease_rag_worker_thread.start()
tea_recovery_tracker_worker_thread.start()


def load_user_chat(user_id):
    records = db.get_user_chat_history_by_user_id(user_id)
    data = []
    for record in records:
        # safely build image URL
        image_filename = record.get('imagedataurl') or ''
        image_url = None
        if image_filename:
            full_path = os.path.join('static', 'uploaded_leaves', image_filename)
            if os.path.exists(full_path):  # only include if file actually exists on disk
                image_url = url_for('static', filename='uploaded_leaves/' + image_filename)

        data.append({
            'disease_name': record.get('disease_name', 'Unknown'),
            'confidence':   str(round(record.get('confidence_score', 0), 2) * 100) + '%',
            'treatment':    record.get('treatment', ''),
            'location':     record.get('location', '—'),
            'barcode':      record.get('detection_code', '—'),
            'imageDataUrl': image_url,
            'date':         record.get('date', '—')
        })

    print(data)
    return data

def get_secret_key():
    return Config.SECRET_KEY

def get_session_lifetime():
    return timedelta(hours=Config.SESSION_LIFETIME)

def add_field_to_db(user_id, field_name,field_latitude, field_longitude,field_elevation, tea_variety, plant_age):

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


def get_users_field_details(user_id):
    result=db.get_field_names_by_user_id(user_id)
    return result


def standardize_disease_name(disease_name):
    match disease_name:
        case 'blister_blight':
            return 'Blister Blight'
        case 'brown_blight':
            return 'Brown Blight'
        case 'grey_blight':
            return 'Grey Blight'
        case 'helopeltis':
            return 'Helopeltis'
        case 'red_rust':
            return 'Red Rust'
        case _:
            return disease_name


#scan_id and chat code are the same
def save_data(user_id:int,field_id:int,chat_code:str,latitude:float,longitude:float,elevation:float,disease_name:str,disease_identifier_confidence_score:float,bounding_box:json,severity_level:str,lesion_count:int,
              healthy_leaf_area:float,affected_area:float,image_name:str,RAG_confidence_score:float,generated_advice:str,recovery_percentage=0.00,status='new'):

    #check the chat_code is already exist if result is None it means this is the first time of detection

    # Check if the chat_code already exists
    result=db.get_scan_chat_history_by_chat_code(chat_code)

    added=False
    scan_id = None
    already_there=False
    detection_id=None
    detection_code=None

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

        new_record = db.get_scan_chat_history_by_chat_code(chat_code)
        if new_record:
            scan_id = new_record.get('scan_id')
        else:
            return False, 'Error retrieving new scan ID.'

    user_scan_result = None

    if not already_there:
        try:
            #add the values to user_scan_history which table create relationship between user,field and scan_history_chat tables
            user_scan_result=db.add_user_scan_history(user_id, field_id, scan_id)
        except Exception as e:
            print(e)
        finally:
            if (not user_scan_result) and added:
                # delete the row which is last added
                db.remove_scan_history_chat_by_chat_code(chat_code)
                return False,'Error when linking user to scan history.'

    disease_id = None

    try:
        # get the disease_id for the disease_name
        disease_id=db.get_disease_id_by_disease_name(standardize_disease_name(disease_name))

        #remove the currently added records
        #elimate the function if didn't return any id
    except Exception as e:
        print(e)
    finally:
        if not disease_id:
            if added:
                db.remove_scan_history_chat_by_chat_code(chat_code)
            return False,'Disease mismatch.'


    detection_result = None
    try:

        #get new detection_id and detection_code
        detection_id,detection_code=db.get_new_detection_code()

        # store the output from disease_identifier  and recovery traker
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
    except Exception as e:
        print(e)
    finally:
        if not detection_result:
            if added:
                db.remove_scan_history_chat_by_chat_code(chat_code)
            return False,'Error when adding new detection.'

    recommendation_result = None
    applied_treatment_result = None
    try:
        # get new recommendation_id and recommendation_code
        recommendation_id,recommendation_code=db.get_new_recommendation_code()

        recommendation_result=db.add_recommended_treatment(
            recommendation_id=recommendation_id,
            recommendation_code=recommendation_code,
            generated_advice=generated_advice,
            RAG_confidence_score=RAG_confidence_score
        )
        applied_treatment_result=db.add_applied_treatment(
            detection_id=detection_id,
            recommendation_id=recommendation_id
        )

    except Exception as e:
        print(e)

    finally:
        if not (recommendation_result & applied_treatment_result):
            print('Deleting recommendation...')
            db.remove_detection_by_detection_id(detection_id)
            db.remove_applied_treatment(detection_id)
            if added:
                db.remove_scan_history_chat_by_chat_code(chat_code)
            return False,'Error when storing treatment.'

    print("added to db")
    return True,'Data added successfully.'


def get_weather_data(latitude,longitude):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={Config.OPENWEATHERMAP_API_KEY}")
    response=response.json()
    humidity=response['main']['humidity']
    temperature=response['main']['temp']
    temperature-=273.15
    print(temperature)
    return {'humidity':humidity, 'temperature':temperature}
