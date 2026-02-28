from flask import Flask, render_template, request,jsonify
import os
from tea_disease_identifier import get_disease,get_severity_level
from treatment_recommendations import get_treatment_recommendation


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
            # 3. Save the uploaded file to the server
            upload_folder = './uploaded_images'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(file_path)
            results = predict(image_file.filename)
            print('results', results)

            #model take controll from here and process the image, then return the result to the frontend
            return jsonify({
                'status': results['matched_disease'],
                'confidence': results['confidence_percent'],
                'treatment': results['llm_response']
            }), 200


        
    elif request.method == 'GET':
        return render_template('analayze.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')



def predict(img):
    diesase_name, infection_percentage = get_disease(img)
    #print(f"Disease Name: {diesase_name}, Infection Percentage: {infection_percentage}%")
    severity_level = get_severity_level(infection_percentage)
    print(f"Severity Level: {severity_level}")
    output=get_treatment_recommendation(diesase_name, severity_level)
    return output


if __name__ == '__main__':
    app.run(debug=True)