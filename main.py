import logging
from flask import Flask, render_template, request, jsonify
import controller


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


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
        #latitude=request.form.get('latitude')
        #longitude=request.form.get('longitude')
        #barcode=request.form['barcode']
        #print("barcode",barcode)

        # 2. Check if a file was selected
        if image_file.filename == '':
            print("No file selected for uploading")
            return jsonify({'error': 'No file selected for uploading'}), 400
        
        if image_file:
            results = controller.predict(image_file)
            #print('results', results)
            return jsonify(results), 200

    elif request.method == 'GET':
        # Fetch scan history from  database 
        data=controller.load_user_chat()
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
    app.run(debug=True, host='0.0.0.0')