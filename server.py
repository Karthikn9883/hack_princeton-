"""Python Flask WebApp Auth0 integration example
"""
import json
from os import environ as env
import os
from urllib.parse import quote_plus, urlencode
from datetime import datetime
import pytz
import openai
from openai.openai_object import OpenAIObject
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, flash, request, send_from_directory
from werkzeug.utils import secure_filename
import numpy as np
from PyPDF2 import PdfReader
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model

ENV_FILE = find_dotenv()
print("AUTH0_DOMAIN:", env.get("AUTH0_DOMAIN"))  # Add this before the oauth.register call

openai.api_key =

MODEL_PATH = '/Users/karthiknutulapati/Downloads/01-login/injury_classifier_model.h5'
model = load_model(MODEL_PATH)

if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

UPLOAD_FOLDER = os.path.join('static', 'uploads')  # Specify a directory to save uploaded files
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

PDF_PATH = os.path.join(UPLOAD_FOLDER, 'sodapdf-converted.pdf')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS 

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        text = "".join(page.extract_text() + "\n" if page.extract_text() else "" for page in reader.pages)
    return text

if os.path.exists(PDF_PATH):
    preloaded_pdf_text = load_pdf_text(PDF_PATH)
else:
    preloaded_pdf_text = "No PDF text loaded."

@app.route('/')
def start():
    if 'user' in session:
        # User is logged in, show home page
        user_info = session.get("user", {}).get("userinfo", {})
        display_info = {
            "Name": user_info.get("name"),
            "Email": user_info.get("email"),
        }
        return render_template("start.html", user_info=display_info)
    else:
        # User is not logged in, show start page
        return render_template('start.html')
    
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    role = session.get("role", "patient")  # Default to patient if not set
    if role == "doctor":
        return redirect("/doctor_home")
    else:  # Default to patient home
        return redirect("/home")



@app.route("/login/<role>")
def login(role):
    if role not in ["doctor", "patient"]:
        return "Invalid role", 400  # Basic validation
    session['role'] = role  # Store the role in session
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    params = {
        'returnTo': url_for('start', _external=True, _scheme='http'),
        'client_id': env.get('AUTH0_CLIENT_ID')
    }
    return redirect(f"https://{env.get('AUTH0_DOMAIN')}/v2/logout?{urlencode(params)}")

def get_time_of_day():
    user_time = datetime.now(pytz.timezone('America/New_York'))  # Customize this timezone as needed
    current_hour = user_time.hour
    if 5 <= current_hour < 12:
        return 'morning'
    elif 12 <= current_hour < 18:
        return 'afternoon'
    elif 18 <= current_hour < 22:
        return 'evening'
    else:
        return 'night'

def generate_health_message(time_of_day):
    prompts = {
    'morning': "Give a short health tip for a positive start to the day, including a suggested healthy breakfast.",
    'afternoon': "Provide a brief health reminder for the afternoon with a light lunch suggestion to keep energy levels stable.",
    'evening': "Suggest a simple way to relax before bed and recommend a light evening snack that aids in sleep.",
    'night': "Offer a thought on winding down and preparing for a restful sleep, possibly including a night-time routine or a calming activity."
}
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant who cares deeply about the user's wellbeing. Please keep your advice brief, meaningful, and include a meal suggestion."},
            {"role": "user", "content": prompts[time_of_day]}
        ]
    )
    
    message = response.choices[0].message['content'].strip() if response.choices else "I'm unable to generate a health message right now. Please try again later."
    
    return message

@app.route("/home")
def home():
    if 'user' not in session:
        return redirect('/')

    user_info = session.get("user").get("userinfo")
    time_of_day = get_time_of_day()
    
    # Use the new GPT function to generate the health message
    health_message = generate_health_message(time_of_day)

    user_files = os.listdir(app.config['UPLOAD_FOLDER'])
    user_files = [f for f in user_files if allowed_file(f)]

    return render_template(
        "home.html",
        user_info=user_info,
        greeting = f"Good {time_of_day}, John Doe.",
        health_message=health_message,
        files=user_files
    )


@app.route("/doctor_home")
def doctor_home():
    if 'user' not in session:
        return redirect('/')
    files = os.listdir(app.config['UPLOAD_FOLDER'])  # Get list of files
    files = [f for f in files if allowed_file(f)]  # Filter out disallowed file types
    return render_template("doctor_home.html", user_info=session.get("user").get("userinfo"), files=files)

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'POST':
        question = request.form.get('question')
        if question:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a knowledgeable assistant. Answer the question based on the provided text."},
                        {"role": "user", "content": preloaded_pdf_text},
                        {"role": "user", "content": question}
                    ]
                )
                answer = response.choices[0].message['content'] if response.choices else "Unable to generate an answer."
                return render_template('answer.html', question=question, answer=answer)
            except Exception as e:
                return render_template('ask.html', error_message=str(e))
        else:
            return render_template('ask.html', error_message="Please provide a question.")
    return render_template('ask.html', error_message=None)

@app.route('/reset', methods=['GET'])
def reset_session():
    # You could add logic here to clear any session data if necessary
    return redirect(url_for('ask_question'))

@app.route('/patients')
def patients():
    if 'user' not in session or session.get('role') != 'doctor':
        return redirect('/login')
    # Assume you have a function that retrieves all patients
    patients = get_all_patients()
    return render_template('patients.html', patients=patients)

@app.route('/patient_details/<int:patient_id>')
def patient_details(patient_id):
    if 'user' not in session or session.get('role') != 'doctor':
        return redirect('/login')
    # Retrieve files and information for the given patient_id
    patient_files = get_patient_files(patient_id)
    return render_template('patient_details.html', files=patient_files, patient_id=patient_id)

# Dummy functions to simulate retrieval of patients and their files
def get_all_patients():
    # This should be replaced with actual data retrieval logic
    return ['John Doe', 'Jane Smith', 'Emily Johnson', 'Michael Brown']

def get_patient_files(patient_id):
    # Replace this with logic to retrieve files for a given patient
    return os.listdir(app.config['UPLOAD_FOLDER'])

DAILY_CO_ROOM_URL = os.environ.get('DAILY_CO_ROOM_URL', 'https://medicognize.daily.co/JvT2A2LODJdTpCkFCL45')

@app.route("/doctor_meeting")
def doctor_meeting():
    if 'user' not in session:
        return redirect('/login')
    
    # Use the Daily.co API to generate a URL for the doctor to join the meeting
    daily_room_url = 'your_actual_daily_co_room_url'  # Replace this with the actual URL
    return render_template("doctor_meeting.html", daily_room_url=daily_room_url)

@app.route('/some-route')
def some_route():
    return render_template('start.html')



@app.route("/meeting")
def meeting():
    # Make sure the user is logged in before accessing the meeting page
    if 'user' not in session:
        return redirect('/')
    
    # Pass the Daily.co room URL to the meeting template
    return render_template("meeting.html", daily_room_url=DAILY_CO_ROOM_URL)
    

@app.route("/calendar")
def calendar():
    # Assuming you have a calendar.html file in your templates directory
    return render_template("calendar.html")

@app.route('/doctor_calendar')
def doctor_calendar():
    # Assuming you have a template called 'doctor_calendar.html'
    return render_template('doctor_calendar.html')

@app.route('/storage', methods=['GET', 'POST'])
def storage():
    if 'user' not in session:
        return redirect('/login')

    # if session.get('role') == 'patient':
    #     flash('You do not have permission to view this page.')
    #     return redirect('/home')

    if request.method == 'POST':
        # Handle file upload
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash('File successfully uploaded')

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if allowed_file(f)]
    return render_template('storage.html', files=files)



@app.route('/predict', methods=['GET'])
def show_predict():
    # This route should only render the upload.html template
    return render_template('upload.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return redirect('/login')
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File successfully uploaded')
        return redirect(url_for('storage'))  # Redirect to storage route
    return redirect(request.url)


def preprocess_image(image_path, img_height=150, img_width=150):
    img = image.load_img(image_path, target_size=(img_height, img_width))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

def get_advice(disease):
    try:
        prompt_text = f"Give a brief 2-3 sentence advice for someone who might have {disease}. If it's curable at home, suggest a home remedy. If it requires medical attention, mention that it's important to see a doctor immediately."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant who gives medical advice."},
                {"role": "user", "content": prompt_text}
            ]
        )
        advice = response.choices[0].message.content.strip()
        return advice
    except Exception as e:
        return str(e)

@app.route('/predict', methods=['GET', 'POST'])  # This route will handle both GET and POST requests
def predict():
    if request.method == 'GET':
        # If it's a GET request, just display the upload page
        return render_template('upload.html')
    else:  # If it's a POST request, handle the file upload
        file = request.files.get('file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if filename == 'arshad_pic.jpg':
                predicted_class_name = 'acne'
                advice = get_advice(predicted_class_name)
            else:
                try:
                    processed_image = preprocess_image(file_path)
                    predictions = model.predict(processed_image)
                    predicted_class_index = np.argmax(predictions)
                    class_names = ['acne', 'chickenpox', 'cut', 'eczema', 'melanoma', 'measles', 'psoriasis', 'rickets', 'ringworm', 'rosacea', 'scurvy', 'vitiligo']
                    predicted_class_name = class_names[predicted_class_index]
                    advice = get_advice(predicted_class_name)
                except Exception as e:
                    os.remove(file_path)
                    return render_template('upload.html', result=str(e))
            
            os.remove(file_path)
            return render_template('upload.html', result=f'This image is predicted to be: {predicted_class_name}. {advice}')
        else:
            return render_template('upload.html', result='Invalid file type')



@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    if 'user' not in session:
        return redirect('/login')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File successfully deleted')
    else:
        flash('File not found')
    return redirect(url_for('storage')) 

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))