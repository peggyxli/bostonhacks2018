from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

import requests
import xml.etree.ElementTree as ET
import time

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/alarm', methods=['GET', 'POST'])
def alarm():
    xml = """<key state="release" sender="Gabbo">PRESET_1</key>"""
    headers = {'Content-Type': 'application/xml'} # set what your server accepts
    requests.post('http://192.168.43.32:8090/key', data=xml, headers=headers)

    time.sleep(2)
    response_xml_as_string = requests.get('http://192.168.43.32:8090/now_playing', data=xml, headers=headers).text
    root = ET.fromstring(response_xml_as_string)
    while root.attrib['source'] != 'STANDBY':
        time.sleep(2)
        response_xml_as_string = requests.get('http://192.168.43.32:8090/now_playing', data=xml, headers=headers).text
        root = ET.fromstring(response_xml_as_string)
        print ('hi')

    time.sleep(2)
    # xml = """<play_info><app_key>fhlvYKfsanEBDRGpFmezAM2iRM7ZuHA7</app_key><url>http://d9b42025.ngrok.io/static/audio/hello_world.mp3</url><service>service text</service><reason>reason text</reason><message>message text</message><volume>50</volume></play_info>"""
    # requests.post('http://192.168.43.32:8090/speaker', data=xml, headers=headers)
    return 'done'
