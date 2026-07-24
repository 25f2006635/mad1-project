from flask import render_template, request, redirect, url_for
from flask import current_app as app
from models import *


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin_login', methods=["GET", "POST"])
def admin_signin():
    if request.method =="POST":
        uname = request.form.get("emailid")  #data from form
        pwd = request.form.get("pwd")
        user=db.session.query(User_Details).filter(User_Details.email==uname, User_Details.password==pwd).first()
        if user and user.role==0:
            return redirect(url_for('admin_dash'))
        else:
            return ("You are not an Admin!")
    return render_template('admin_login.html')

@app.route('/staff_login', methods=["GET", "POST"])
def staff_signin():
    if request.method =="POST":
        uname = request.form.get("emailid")  #data from form
        pwd = request.form.get("pwd")
        user=db.session.query(User_Details).filter(User_Details.email==uname, User_Details.password==pwd).first()
        if user and user.role==1:
            return redirect(url_for('staff_dash'))
        else:
            return ("You are not a Staff, please register yourself first!")
    return render_template('staff_login.html')

@app.route('/user_login', methods=["GET", "POST"])
def user_signin():
    if request.method =="POST":
        uname = request.form.get("emailid")  #data from form
        pwd = request.form.get("pwd")
        user=db.session.query(User_Details).filter(User_Details.email==uname, User_Details.password==pwd).first()
        if user and user.role==2:
            return redirect(url_for('user_dash'))
        else:
            return ("You are not an User, please register yourself first!")
    return render_template('user_login.html')


@app.route('/signup', methods=["GET","POST"])
def register():
    if request.method=="POST":
        uname = request.form.get("emailid")  #data from form
        pwd = request.form.get("pwd")
        role=request.form.get("utype")
        exists=db.session.query(User_Details).filter(User_Details.email==uname).first()
        if exists:
            return render_template("signup.html", error="Email is already registered!")
        else:
            #need to store in user_details
            ud = User_Details(email=uname, password=pwd,role=int(role))
            db.session.add(ud)
            db.session.commit() #save in the db


    return render_template("signup.html")





@app.route('/admin')
def admin_dash():
    return render_template("admin_dash.html")

@app.route('/staff')
def staff_dash():
    return render_template("staff_dash.html")

@app.route('/user')
def user_dash():
    return render_template("user_dash.html")


