from flask import Flask, render_template, request, jsonify, url_for
from db import Database
import os


db=Database()
app = Flask(__name__)


user_id='1'

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analayze', methods=['GET', 'POST'])
def analayze():
    if request.method == 'POST':

        # 1. Check if the request contains the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
    
        image_file = request.files['image']

        # 2. Check if a file was selected
        if image_file.filename == '':
            return jsonify({'error': 'No file selected for uploading'}), 400
        
        if image_file:
            # 3. Save the uploaded file to the server
            upload_folder = './static/uploaded_leaves'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(file_path)
            #results = predict(image_file.filename)
            # print('results', results)
            return jsonify({
                'status': 'Disease Detected: Powdery Mildew',
                'confidence': '94.5%',
                'treatment': 'Remove infected leaves. Apply a sulfur-based fungicide or neem oil spray directly to the foliage.'
            }), 200

    elif request.method == 'GET':
        # ── Fetch scan history from your database ──
        records = db.get_user_chat_history_by_user_id(user_id)
        print(records)
        data=[]
        for record in records:
            data.append(
                {
                    'disease_name': record['disease_name'],
                    'confidence': str(round(record['confidence_score'],2)*100)+'%',
                    'treatment': record['treatment'],
                    'location': record['location'],
                    'barcode': record['detection_code'],
                    'imageDataUrl': url_for('static', filename='uploaded_leaves/'+record['imagedataurl']),
                    'date': record['date']
                }
            )
        print(data)

        return render_template('analayze.html', records=data)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

















if __name__ == '__main__':
    app.run(debug=True)