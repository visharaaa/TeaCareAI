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
            # model takes control from here and processes the image
            return jsonify({
                'status': 'Disease Detected: Powdery Mildew',
                'confidence': '94.5%',
                'treatment': 'Remove infected leaves. Apply a sulfur-based fungicide or neem oil spray directly to the foliage.'
            }), 200

    # elif request.method == 'GET':
    #     # ── Fetch scan history from your database ──
    #     raw_records = db.execute(
    #         "SELECT status, confidence, treatment, location, barcode, image_url, date FROM scans ORDER BY date DESC"
    #     ).fetchall()

    #     # Convert each row to a plain dictionary so Jinja2 can serialize it
    #     records = [dict(row) for row in raw_records]

    #     return render_template('analayze.html', records=records)

    elif request.method == 'GET':
        # ── Static test records ──
        records = [
            {
                'status':     'Disease Detected: Powdery Mildew',
                'confidence': '94.5%',
                'treatment':  'Remove infected leaves. Apply a sulfur-based fungicide or neem oil spray directly to the foliage.',
                'location':   'Greenhouse A, Row 3',
                'barcode':    'PLT-20240601-007',
                'image_url':  '',
                'date':       '2024-06-01 14:32'
            },
            {
                'status':     'Healthy',
                'confidence': '98.1%',
                'treatment':  'No treatment needed. Continue regular watering and monitoring.',
                'location':   'Greenhouse B, Row 1',
                'barcode':    'PLT-20240602-012',
                'image_url':  '',
                'date':       '2024-06-02 09:15'
            },
            {
                'status':     'Disease Detected: Leaf Blight',
                'confidence': '87.3%',
                'treatment':  'Prune affected areas immediately. Apply copper-based fungicide every 7 days for 3 weeks.',
                'location':   'Field C, Section 2',
                'barcode':    'PLT-20240603-019',
                'image_url':  '',
                'date':       '2024-06-03 11:47'
            },
            {
                'status':     'Disease Detected: Root Rot',
                'confidence': '91.0%',
                'treatment':  'Improve drainage. Remove and destroy infected roots. Treat soil with a phosphonate fungicide.',
                'location':   'Field A, Section 5',
                'barcode':    'PLT-20240604-023',
                'image_url':  '',
                'date':       '2024-06-04 16:05'
            },
            {
                'status':     'Healthy',
                'confidence': '96.7%',
                'treatment':  'No treatment needed. Plant looks strong — maintain current care routine.',
                'location':   'Greenhouse A, Row 7',
                'barcode':    'PLT-20240605-031',
                'image_url':  '',
                'date':       '2024-06-05 08:20'
            },
        ]

    return render_template('analayze.html', records=records)


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