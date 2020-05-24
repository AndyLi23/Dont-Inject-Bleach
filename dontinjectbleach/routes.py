from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from dontinjectbleach.backend.corona import updateCorona
from dontinjectbleach.backend.corona_news import updateCoronaNews
from dontinjectbleach.backend.condense_corona import condense_corona
import csv, json
from random import randint
from numpy.random import permutation
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from nltk.sentiment.util import *
from datetime import datetime
from dontinjectbleach.backend.hospital import search

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

@routes.route("/trackerdata")
@login_required
def trackerdata():

    prevscore = -1
    if current_user.symptoms:
        prevscore = float(current_user.symptoms.split("^!@")[-2].split("[][]")[1])

    data = []
    data.append(["Timestamp", "AI Rating"])

    for a in current_user.symptoms.split("^!@"):
        if a != "":
            data.append([a.split("[][]")[0], a.split("[][]")[1]])

    print(prevscore)

    return render_template("trackerdata.html", prev_score=prevscore, stam=json.dumps(data))


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
    data = ""
    with open('dontinjectbleach/corona-data/json_corona.json') as json_file:
        data = json.load(json_file)
    # with open("dontinjectbleach/corona-data/corona_condensed1.txt") as fin:
    #     data += fin.read()
    # with open("dontinjectbleach/corona-data/corona_condensed2.txt") as fin:
    #     data += fin.read()
        
    return render_template('corona.html', news=news, data=data)

@routes.route('/hospital')
def selddiog():
    return render_template('hospital.html', place="", s=False)

@routes.route('/selfdiagnosis')
def hospital():
    return render_template('selfdiagnosis.html')

@routes.route('/selfdiagnosis', methods=['POST'])
def selfdiag_post():

    arr = [7,8,10,6,6,4,7,4,2]

    avg = 0
    for i in range(9):
        if request.form.get("box%s" % str(i+1)) != None:
            avg += arr[i]
    totalAvg = avg / sum(arr)
        
    return render_template('selfdiagnosis.html', avg=round(totalAvg, 2))

@routes.route('/hospital', methods=['POST'])
def hospital_post():
    place = request.form.get('place')
    s = search(place)
    print(s)
    if place:
        return render_template('hospital.html', place=s, s=True)
    return render_template('hospital.html', place="", s=False)


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