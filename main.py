from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from webforms import UserForm, LoginForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user 

# Create a Flask Instance
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = "1234"

# Create Database instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2009ih43@localhost/accounts'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create Table Model
class Users(UserMixin, db.Model):
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


@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# Create a route decorator for home page
@app.route('/')
@login_required
def home_page():
	flash(f"Welcome!! {current_user.username} ")
	return render_template("home.html")

# Create route for sign up page
@app.route('/create-account', methods=["GET", "POST"])
def create_account():
	# import user form
	form = UserForm()

	# add user to database and check if user is already in database
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()

		if user is None:
			hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
			new_user = Users(username=form.username.data, email=form.email.data, password=form.password_hash.data)
			db.session.add(new_user)
			db.session.commit()

			# clear fields
			form.username.data = ''
			form.email.data = ''
			form.password_hash.data = ''

			flash("User Added Successfully!")

			return redirect(url_for('home_page'))

	our_users = Users.query.order_by(Users.id)
	return render_template("create_account.html", form=form, our_users=our_users)


# Create login route page
@app.route('/login', methods=["GET", "POST"])
def login():
	# import login form
	form = LoginForm()

	# Validation
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				return redirect(url_for('home_page'))
			else:
				flash("Wrong Password - Try Again!")
		else:
			flash("Hey that user doesn't exist! Try Again...")

	return render_template("login.html", form=form)


@app.route('/delete/<int:id>')
def delete(id):
	form = UserForm()
	user_to_delete = Users.query.get_or_404(id)

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("user deleted Successfully")

		our_users = Users.query.order_by(Users.id)
		return render_template("create_account.html", form=form, our_users=our_users)

	except:

		flash("problem deleting user")
		return render_template("create_account.html", form=form, our_users=our_users)





# Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404