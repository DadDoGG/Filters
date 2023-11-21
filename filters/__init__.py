from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfgdfg23423j2bf3kj2lh34g54t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/filters'
db = SQLAlchemy(app)
manager = LoginManager(app)
api = Api(app)

from filters import models, routes, admin, views

with app.app_context():
    db.create_all()
