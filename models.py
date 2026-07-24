from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User_Details(db.Model):
    __tablename__='user_details' #user defind name
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique = True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False)  #0-admin, 1-staff, 2-trekker
    #Relation column linking parent to child
    trekkers=db.relationship("Trekker", cascade="all,delete", backref="user_details")
    staff=db.relationship("Staff", cascade="all,delete", backref="user_details")

class Trekker(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=False) #linking child to parent
    full_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)  #0-registered, 1-deactivated, 2- blacklisted

class Staff(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=False) #linking child to parent
    full_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    # assigned_trek_id = db.Column(db.Integer, db.ForeignKey(''), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)  #0-registered, 1-approved, 2-rejected, 3-deactivated, 4- blacklisted
    

