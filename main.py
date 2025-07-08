from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from webforms import UserForm, LoginForm

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
	password_hash = db.Column(db.String(300))

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

	def	verify_password(self, password):
		return check_password_hash(self.password_hash, password)

# Create a route decorator
@app.route('/')
def home_page():
	flash("Welcome!!")
	return render_template("home.html")

@app.route('/create-account', methods=["GET", "POST"])
def create_account():
	form = UserForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()

		if user is None:
			hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
			new_user = Users(username=form.username.data, email=form.email.data, password=form.password_hash.data)
			db.session.add(new_user)
			db.session.commit()

			form.username.data = ''
			form.email.data = ''
			form.password_hash.data = ''

			flash("User Added Successfully!")

	our_users = Users.query.order_by(Users.id)
	return render_template("create_account.html", form=form, our_users=our_users)



@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password_hash, form.password.data):
				return redirect(url_for('home_page'))
			else:
				flash("Wrong Password - Try Again!")
		else:
			flash("Hey that user doesn't exist! Try Again...")

	return render_template("login.html", form=form)

# Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404