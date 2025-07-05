from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create a Flask Instance
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = "1234"

# Create Database instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2009ih43@localhost/accounts'
db = SQLAlchemy(app)

# Create Table Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	email = db.Column(db.String(120), nullable=False, unique=True)
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def	verify_password(self, password):
		return check_password_hash(self.password_hash, password)

# Create a route decorator
@app.route('/')

def home_page():
	return render_template("home.html")

# Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404