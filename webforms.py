from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField
from wtforms.validators import DataRequired, EqualTo

class UserForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	password_hash = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Login")

class MatchReportForm(FlaskForm):
    title = StringField('Match Title', validators=[DataRequired()])
    date = DateField('Match Date', validators=[DataRequired()])
    home_team = StringField('Home Team', validators=[DataRequired()])
    away_team = StringField('Away Team', validators=[DataRequired()])
    match_score = StringField('Match Score')
    possession = StringField('Possession Stats')
    motm = StringField('Man of the Match')

    # These hidden fields will contain serialized JSON from JS
    home_players_json = HiddenField()
    away_players_json = HiddenField()

    submit = SubmitField('Save Match Report')
    export = SubmitField('Export to Excel')