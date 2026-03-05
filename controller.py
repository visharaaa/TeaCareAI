from flask import url_for
from app.database.db import Database
from app.services.tea_disease_identifier import TeaDiseaseIdentifier
from app.services.treatment_recommendations import TeaDiseaseRAG
from config import Config
import os
from datetime import datetime
import threading
import queue

db = Database()
user_id=1


threading_lock= threading.Lock()
vision_queue = queue.Queue()
rag_queue = queue.Queue()



def tea_disease_identifier_worker():
    print("Background TeaDiseaseIdentifier worker starting...")

    # Load the model into new object
    tea_disease_identifier=TeaDiseaseIdentifier('./app/models/tea_disease_identifier_weight.pt','./static/uploaded_leaves')

    print("TeaDiseaseIdentifier Model loaded successfully! Worker is ready.")

    while True:

        #get the next image  from the queue
        file_path,response_queue=vision_queue.get()

        # Wait for the tread to be completely free
        with threading_lock:
            try:
                # Process the one image.
                disease_name,infection_percentage,severity_level=tea_disease_identifier.get_disease(file_path)

                result=(disease_name,infection_percentage,severity_level)

                # Put the result into this specific user's private pager
                response_queue.put(result)

            except Exception as e:
                # If the model crashes on a bad image, send the error back
                response_queue.put(Exception(f"Error processing image: {str(e)}"))


        # Tell the main waiting room this task is officially done
        vision_queue.task_done()





def predict(img, latitude=10, longitude=20,elevation=2):
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)

    #chat_code=generate_unique_code('chat')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{img.filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    img.save(file_path)

    # Create a private pager just for THIS specific web request
    response_queue = queue.Queue()

    # Put the filename and the private pager into the task_queue
    vision_queue.put((filename, response_queue))

    # The Flask route pauses right here and waits for the worker to finish the math
    result = response_queue.get()

    # check: Did the worker return an error?
    if isinstance(result, Exception):
        print(f"Prediction failed: {result}")
        return {'error': 'Failed to process image'}

    #print(result)
    disease_name, infection_percentage, severity_level,*extra_stuff = result

    # save to database
    try:
        #db.add_scan_history_chat(chat_code=generate_code('chat'),timestamp=datetime.now(),latitude=latitude,longitude=longitude,elevation=elevation)
        print("added to db")
    except Exception as e:
        print(f"Warning: could not save to DB: {e}")

    result = {
        'status':     disease_name,
        'confidence': str(infection_percentage) + '%',
        'treatment':  'Remove infected leaves. Apply a sulfur-based fungicide or neem oil spray directly to the foliage.'
    }
    return result



def tea_disease_rag_worker():
    print("Background TeaDiseaseRAG worker starting...")

    # Load the model into new object
    tea_disease_rag=TeaDiseaseRAG(Config.KB_PATH,Config.VECTOR_DB_PATH)

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

        vision_queue.task_done()




#initialize the threads
tea_disease_identifier_worker_thread = threading.Thread(target=tea_disease_identifier_worker, daemon=True) ## daemon=True means this thread will automatically shut down when kill the Flask server
tea_disease_rag_worker_thread=threading.Thread(target=tea_disease_rag_worker,daemon=True)

#start the threads in background processing
tea_disease_identifier_worker_thread.start()
tea_disease_rag_worker_thread.start()




































def load_user_chat():
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





#params=>none
#this function read the code.txt to get the last code of each type
#return=>dict
def load_codes():
    with open('./code.txt', 'r') as f:
        id['chat_code'] = int(f.readline())
        id['scan_code'] = int(f.readline())
        id['recommendation_code'] = int(f.readline())
        id['detection_code'] = int(f.readline())
    return id

#params=>none
#this function write the code.txt to save the last code of each type
def save_codes(id):
    with open('./code.txt', 'w') as f:
        f.write(str(id['chat_code']) + '\n')
        f.write(str(id['scan_code']) + '\n')
        f.write(str(id['recommendation_code']) + '\n')
        f.write(str(id['detection_code']) + '\n')


code_lock = threading.Lock()
generate_unique_code_lock = threading.Lock()

def generate_unique_code(code_type):
    with generate_unique_code_lock:
        try:    
            # 1. Load current codes
            codes = load_codes()
        except Exception as e:
            print(f"Warning: could not load codes: {e}")
            codes = {'chat_code': 0, 'scan_code': 0, 'recommendation_code': 0, 'detection_code': 0}
        
        # 2. Increment the specific counter
        if code_type == 'chat':
            codes['chat_code'] += 1
            new_code = f"C_{codes['chat_code']:09d}"
        elif code_type == 'scan':
            codes['scan_code'] += 1
            new_code = f"S_{codes['scan_code']:09d}"
        elif code_type == 'recommendation':
            codes['recommendation_code'] += 1
            new_code = f"R_{codes['recommendation_code']:09d}"
        elif code_type == 'detection':
            codes['detection_code'] += 1
            new_code = f"D_{codes['detection_code']:09d}"
        else:
            raise ValueError("Invalid code type")
            
        # 3. Save updated codes
        save_codes(codes)
    return new_code



