from flask import Flask
from models import db

app = None
#creating configuration between app, controller and db model
def setup_app():
    app = Flask(__name__)
    app.secret_key = 'secret'
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


from controller import *
if __name__=="__main__":
    app.run(debug=True)


