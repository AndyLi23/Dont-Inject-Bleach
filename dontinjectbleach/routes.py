from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from dontinjectbleach.backend.corona import updateCorona
from dontinjectbleach.backend.corona_news import updateCoronaNews
import csv

routes = Blueprint('routes', __name__)

@routes.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    return render_template("index.html")

@routes.route("/about")
def about():
    return render_template("about.html")

@routes.route('/login')
def login():
    return render_template('login.html')

@routes.route('/home')
@login_required
def home():
    return render_template("home.html")

@routes.route('/login', methods=['POST'])
def login_post():

    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('routes.login'))


    login_user(user, remember=remember)
    return redirect(url_for('routes.home'))

@routes.route('/signup')
def signup():
    return render_template('signup.html')

@routes.route('/coronavirus')
def corona():
    updateCorona()
    updateCoronaNews()
    temp = []
    with open("dontinjectbleach/corona-data/news.csv", "r") as fin:
        reader = csv.reader(fin, delimiter=',')
        l = 0
        labels = []
        news = []
        for i in reader:
            if l == 0:
                labels = i
                l += 1
            else:
                temp = {}
                for k in range(len(i)):
                    temp[labels[k]] = i[k]
                news.append(temp)
                                     
    return render_template('corona.html', news=news)

@routes.route('/hospital')
def selddiog():
    return render_template('hospital.html')

@routes.route('/selfdiagnosis')
def hospital():
    return render_template('selfdiagnosis.html')

@routes.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('routes.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('routes.login'))

@routes.route('/signout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))