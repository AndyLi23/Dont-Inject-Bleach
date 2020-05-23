from flask import Flask
import os

app = Flask(__name__)

from .routes import routes as routes_blueprint
app.register_blueprint(routes_blueprint)