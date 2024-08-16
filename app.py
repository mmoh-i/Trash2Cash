import pathlib
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import requests
import json
import os
import logging
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2 import WebApplicationClient
import google.auth.transport.requests
from dotenv import load_dotenv
from urllib.parse import urlencode
from flask import session
from authlib.integrations.flask_client import OAuth
import traceback
import uuid

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from db import db, User, init_db

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

app = Flask(__name__)
oauth = OAuth(app)
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template('index.html') if current_user.is_authenticated else render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    email = request.form['email']
    message = request.form['message']
    print(f"Received message from {email}: {message}")
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password is None:
                flash("please login with google")
            elif check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    else:
        flash("invalid email")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"status": "error", "message": "Email address already exists"})
        else:
            new_user = User.create(
                name=name,
                email=email,
                password=generate_password_hash(password, method='sha256')
            )
            login_user(new_user)
            return jsonify({"status": "success"})
    return render_template('signup.html', google_client_id=GOOGLE_CLIENT_ID)

@app.route('/google_login')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route('/google_login/callback')
def callback():
    try:
        code = request.args.get("code")
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        print("Token Response:", token_response.text)
        
        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        print("User Info Response:", userinfo_response.text)

        if userinfo_response.json().get("email_verified"):
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]

            user = User.query.filter_by(email=users_email).first()
            if not user:
                user = User.create(
                    name=users_name,
                    email=users_email,
                    profile_pic=picture
                )

            login_user(user)
            return redirect(url_for("home"))
        else:
            return "User email not available or not verified by Google.", 400
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in callback: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return f"An error occurred during authentication. Error: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)