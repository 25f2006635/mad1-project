from flask import Flask
from models import db, User_Details
from config import *
from flask_login import LoginManager


app = None
login_manager = None
#creating configuration between app, controller and db model
def setup_app():
    global app, login_manager
    app = Flask(__name__)

    #Configure login manager
    app.config["SECRET_KEY"]=SECRET_KEY
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    #Data base settings
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///trek.sqlite3"
    db.init_app(app)  #linking between db and flask
    app.app_context().push()   #giving access of my current app to other modules
    print("Setup is done!")

# to create pre-defined admin, commands in terminal
# admin= User_Details(user_id=0, email="trek_admin@123.com", password=12345, role=0)
# db.session.add(admin)
# db.session.commit()
      

#executable of flask
setup_app()  #calling

@login_manager.user_loader
def load_user(user_id):
    return User_Details.query.get(int(user_id))


from controller import *

if __name__=="__main__":
    app.run(debug=True)


