from flask import Flask, render_template, request,jsonify
from isort import file

app = Flask(__name__)

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
            #model take controll from here and process the image, then return the result to the frontend
            return jsonify({
                'status': 'Disease Detected: Powdery Mildew',
                'confidence': '94.5%',
                'treatment': 'Remove infected leaves. Apply a sulfur-based fungicide or neem oil spray directly to the foliage.'
            }), 200

    elif request.method == 'GET':
        return render_template('analayze.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

















if __name__ == '__main__':
    app.run(debug=True)