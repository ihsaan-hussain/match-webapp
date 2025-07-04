from flask import Flask, render_template

# Create a Flask Instance
app = Flask(__name__)

# Create a route decorator
@app.route('/')

def home_page():
	return "<h1>Home Page</h1>"