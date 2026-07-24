from flask import render_template
from flask import current_app as app

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin_login')
def signin():
    return render_template("admin_login.html")

@app.route('/signup')
def register():
    return render_template("signup.html")

@app.route('/admin')
def admin_dash():
    return render_template("admin_dash.html")


