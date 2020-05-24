from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from dontinjectbleach.backend.corona import updateCorona
from dontinjectbleach.backend.corona_news import updateCoronaNews
import csv
from random import randint
from numpy.random import permutation
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from nltk.sentiment.util import *
from datetime import datetime

routes = Blueprint('routes', __name__)

def analyze_sentiment(text_content):
    sid = SentimentIntensityAnalyzer()

    ss = sid.polarity_scores(text_content)
    for k in sorted(ss):
        if k == "compound":
            return ss[k]


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
    # pt = 
    if current_user.symptoms:
        prev_time_min = current_user.symptoms.split("^!@")[-2].split("[][]")[0].split(" ")[1].split(":")[1]
        prev_time_hr = current_user.symptoms.split("^!@")[-2].split("[][]")[0].split(" ")[1].split(":")[0]
        prev_time_day = current_user.symptoms.split("^!@")[-2].split("[][]")[0].split(" ")[0].split("-")[1]

        # t = str(datetime.today()).split(".")[0].split(" ")
        # time_now, time_now_hr, time_now_day = t[1], t[0], t[0]
        time_now_min = str(datetime.today()).split(".")[0].split(" ")[1].split(":")[1]
        time_now_hr = str(datetime.today()).split(".")[0].split(" ")[1].split(":")[0]
        time_now_day = str(datetime.today()).split(".")[0].split(" ")[0].split("-")[1]
        
        ten_passed = abs((int(time_now_hr)*60 + int(time_now_min)) - (int(prev_time_hr)*60 + int(prev_time_min))) > 10

        return render_template("home.html", ten_passed=ten_passed)
    return render_template("home.html", ten_passed=True)

@routes.route('/home', methods=['POST'])
def home_post():
    text = request.form.get('fname')

    val = analyze_sentiment(text)
    simp = current_user.symptoms
    "YYYY-MM-DD HR:MIN:SEC"
    d = str(datetime.today()).split(".")[0]
    current_user.symptoms += d + "[][]" + str(val) + "^!@"
    db.session.commit()
    
    return render_template("home.html", sentiment=val, ten_passed=False)

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
    
    idx = randint(0, len(news)-10)
    news = list(permutation(news[idx:idx+10]))
    
    data = {}
    with open("dontinjectbleach/corona-data/data.csv", "r") as fin:
        l = fin.readline()
        for row in fin.read().split("\n")[:-1]:
            temp = {}
            r = []
            i = 0
            for j in range(len(row)):
                if j == len(row)-1:
                    r.append(row[i:j+1])
                elif row[j] == "," and row[j+1] != " ":
                    r.append(row[i:j])
                    i = j+1
            temp["active"], temp["recovered"], temp["dead"], temp["confirmed"] = r[-2], r[-3], r[-4], r[-5]
            if r[-1][0] == "\"":
                z = r[-1][1:-1]
            else:
                z = r[-1]
            for i in range(len(z.split(", "))):
                if ", ".join(z.split(", ")[i:]) not in data.keys():
                    data[", ".join(z.split(", ")[i:])] = temp
                else:
                    prev = data[", ".join(z.split(", ")[i:])]
                    new = {}
                    new["active"] = str(int(temp["active"]) + int(prev["active"]))
                    new["recovered"] = str(int(temp["recovered"]) + int(prev["recovered"]))
                    new["dead"] = str(int(temp["dead"]) + int(prev["dead"]))
                    new["confirmed"] = str(int(temp["confirmed"]) + int(prev["confirmed"]))
                    data[", ".join(z.split(", ")[i:])] = new
    
    return render_template('corona.html', news=news, data=data)

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

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), symptoms="")

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('routes.login'))

@routes.route('/signout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))