from flask import Flask, render_template, flash, redirect, url_for, request, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from webforms import UserForm, LoginForm, MatchReportForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user 
from export_as_excel import create_excel
from flask_migrate import Migrate
import json

# Create a Flask Instance
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = "1234"

# Create Database instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2009ih43@localhost/accounts'
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

# Create Table Model
class Users(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	email = db.Column(db.String(120), nullable=False, unique=True)
	password_hash = db.Column(db.String(300))
	matches = db.relationship('MatchReport', backref='author', lazy=True)

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

	def	verify_password(self, password):
		return check_password_hash(self.password_hash, password)

class MatchReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_json = db.Column(db.Text)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# Create a route decorator for home page
@app.route('/')
@login_required
def home_page():
	#flash(f"Welcome!! {current_user.username} ")
	matches = MatchReport.query.filter_by(account_id=current_user.id).all()
	return render_template("home.html", matches=matches)

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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

'''
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
'''

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_match():
    form = MatchReportForm()
    if form.validate_on_submit():
        data = {
            'home_team': form.home_team.data,
            'away_team': form.away_team.data,
            'match_score': form.match_score.data,
            'possession': form.possession.data,
            'motm': form.motm.data,
            'home_players': json.loads(form.home_players_json.data or '[]'),
            'away_players': json.loads(form.away_players_json.data or '[]')
        }
        match = MatchReport(
            title=form.title.data,
            date=form.date.data,
            account_id=current_user.id,
            data_json=json.dumps(data)
        )
        db.session.add(match)
        db.session.commit()
        if form.export.data:
            return redirect(url_for('export_match', match_id=match.id))
        return redirect(url_for('home_page'))
    return render_template('create_match.html', form=form)

@app.route('/edit/<int:match_id>', methods=['GET', 'POST'])
@login_required
def edit_match(match_id):
    match = MatchReport.query.get_or_404(match_id)
    if match.account_id != current_user.id:
        return "Unauthorized", 403

    data = json.loads(match.data_json)
    form = MatchReportForm(obj=match)
    if request.method == 'GET':
        form.home_team.data = data['home_team']
        form.away_team.data = data['away_team']
        form.match_score.data = data['match_score']
        form.possession.data = data['possession']
        form.motm.data = data['motm']
        form.home_players_json.data = json.dumps(data['home_players'])
        form.away_players_json.data = json.dumps(data['away_players'])

    if form.export.data:
    	return redirect(url_for('export_match', match_id=match.id))

    if form.validate_on_submit():
        match.title = form.title.data
        match.date = form.date.data
        match.data_json = json.dumps({
            'home_team': form.home_team.data,
            'away_team': form.away_team.data,
            'match_score': form.match_score.data,
            'possession': form.possession.data,
            'motm': form.motm.data,
            'home_players': json.loads(form.home_players_json.data),
            'away_players': json.loads(form.away_players_json.data)
        })
        db.session.commit()
        return redirect(url_for('home_page'))

    return render_template('create_match.html', form=form)

@app.route('/delete/<int:match_id>')
@login_required
def delete_match(match_id):
    match = MatchReport.query.get_or_404(match_id)
    if match.account_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(match)
    db.session.commit()
    return redirect(url_for('home_page'))

@app.route('/export/<int:match_id>')
@login_required
def export_match(match_id):
    match = MatchReport.query.get_or_404(match_id)
    if match.account_id != current_user.id:
        return "Unauthorized", 403
    data = json.loads(match.data_json)
    excel_file = create_excel(data)
    return send_file(excel_file, as_attachment=True, download_name=f'match_report_{match.date.strftime('%Y-%m-%d')}.xlsx')

# Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404