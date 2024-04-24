from flask import Flask
from markupsafe import escape
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/user/<username>')
def show_user_profile(username):
    return f'Welcome {escape(username)}!'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
