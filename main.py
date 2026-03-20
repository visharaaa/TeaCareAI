from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import auth
from controller import register_user,load_user_chat,predict,get_secret_key,get_session_lifetime,add_field_to_db,get_users_field_details,generate_new_chat_code

app = Flask(__name__)
app.secret_key = get_secret_key()
app.permanent_session_lifetime = get_session_lifetime()

@app.route('/')
def home():
    user = auth.get_current_user()
    return render_template('index.html', user=user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        data      = request.get_json(silent=True) or request.form
        email     = (data.get('email')    or '').strip()
        password  = (data.get('password') or '').strip()
        device_info = request.headers.get('User-Agent')
        latitude  = data.get('latitude')
        longitude = data.get('longitude')
        if not email or not password:
            if request.is_json:
                return jsonify({'error': 'Email and password are required.'}), 400
            return render_template('login.html', error='Email and password are required.')

        # creating the new session
        user, error = auth.login_user(email, password, device_info=device_info, latitude=latitude, longitude=longitude)

        if error:
            if request.is_json:
                return jsonify({'error': error}), 401
            return render_template('login.html', error=error)

        if request.is_json:
            return jsonify({'message': 'Login successful.', 'user_name': user['user_name']}), 200
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/field/add', methods=['GET', 'POST'])
@auth.login_required
def add_field():

    if request.method == 'POST':
        field_name       = (request.form.get('field_name')or '').strip()
        field_latitude   = request.form.get('field_latitude')
        field_longitude  = request.form.get('field_longitude')
        field_elevation  = request.form.get('field_elevation')
        tea_variety      = (request.form.get('tea_variety')or '').strip()
        plant_age        = request.form.get('plant_age_in_years')

        if not all([field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age]):
            return render_template('add_field.html', error='All fields are required.')

        try:

            field_latitude  = float(field_latitude)
            field_longitude = float(field_longitude)
            field_elevation = float(field_elevation)
            plant_age       = float(plant_age)

        except ValueError:

            return render_template('add_field.html', error='Latitude, longitude, elevation and age must be numbers.')


        user_id   = session["user_id"]

        # add field to the database
        result = add_field_to_db(user_id,field_name,field_latitude, field_longitude,field_elevation, tea_variety, plant_age)

        if not result:
            return render_template('add_field.html', error='Could not save field. It may already exist.')

        return render_template('add_field.html', success=f'Field "{field_name}" registered successfully!')

    return render_template('add_field.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    auth.logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))

    #validating the user inputs
    if request.method == 'POST':
        first_name = (request.form.get('first_name') or '').strip()
        last_name  = (request.form.get('last_name')  or '').strip()
        email      = (request.form.get('email')      or '').strip().lower()
        password   = (request.form.get('password')   or '').strip()
        user_type  = request.form.get('user_type', 'farmer')

        print(password)

        if not all([first_name, last_name, email, password]):
            return render_template('signup.html', error='All fields are required.')

        if len(password) < 8:
            return render_template('signup.html', error='Password must be at least 8 characters.')

        # Set a default value for user_type
        if user_type not in ('farmer', 'agronomist', 'state'):
            user_type = 'farmer'
        
        #registering the user
        status, error = register_user(user_name=f"{first_name} {last_name}",email=email,password=password,user_type=user_type)

        if error:
            return render_template('signup.html', error=error)

        return render_template('signup.html', success='Account created! You can now log in.')

    return render_template('signup.html')

@app.route('/analayze', methods=['GET', 'POST'])
@auth.login_required
def analayze():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        #print(request.form)
        image_file = request.files['image']
        latitude   = request.form.get('latitude')
        longitude  = request.form.get('longitude')
        field_id   = request.form.get('field_id')
        barcode    = request.form.get('barcode')


        if image_file.filename == '':
            return jsonify({'error': 'No file selected for uploading'}), 400

        user_id = session["user_id"]

        #getting the result from tea_disease_identifier,treatment_recommendations and recovery_tracker
        results = predict(user_id,image_file,field_id=field_id,chat_code=barcode, latitude=latitude, longitude=longitude)
        return jsonify(results), 200

    # load the chat history data
    data = load_user_chat(session['user_id'])

    return render_template('analayze.html', records=data)

@app.route('/api/fields', methods=['GET'])
@auth.login_required
def get_fields():
    user_id = session['user_id']
    print(user_id)
    #get the users' field_id and field_name
    fields = get_users_field_details(user_id)
    print(fields)
    return jsonify(fields or [])

@app.route('/api/generate-barcode', methods=['POST'])
@auth.login_required
def generate_barcode():
    barcode=generate_new_chat_code()
    return jsonify({'barcode': barcode})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')