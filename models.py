from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin   #protecting routes

db=SQLAlchemy()

class Trek(db.Model):
    __tablename__='trek'
    trek_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_name = db.Column(db.String, unique = True, nullable = False)
    location = db.Column(db.String, nullable = False)
    difficulty = db.Column(db.Integer, nullable=False, default=0)  #0-easy, 1-moderate, 2- hard
    staff_assigned = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable = False)
    status = db.Column(db.Integer, nullable=False, default=0)  #0-open, 1-closed, 2- completed
    duration = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String, nullable = False)
    av_slots = db.Column(db.Integer, nullable = False)
    st_date = db.Column(db.Date, nullable = False)
    en_date = db.Column(db.Date, nullable = False)
    bookings = db.relationship("Bookings", cascade="all, delete", backref="trek")     
    


class User_Details(db.Model, UserMixin):
    __tablename__='user_details' #user defind name
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique = True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False)  #0-admin, 1-staff, 2-trekker
    #Relation column linking parent to child
    trekker=db.relationship("Trekker", cascade="all,delete", backref="user_details", uselist=False)
    staff=db.relationship("Staff", cascade="all,delete", backref="user_details", uselist=False)
    def get_id(self):
        return str(self.user_id)

class Trekker(db.Model):
    __tablename__='trekker'
    trekker_id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=False, unique=True) #linking child to parent
    full_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)  #0-registered, 1-deactivated, 2- blacklisted
    bookings = db.relationship("Bookings", cascade="all, delete", backref="trekker")

class Staff(db.Model):
    __tablename__='staff'
    staff_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=False, unique=True) #linking child to parent
    full_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)  #0-registered, 1-approved, 2-rejected, 3-deactivated, 4- blacklisted
    treks = db.relationship("Trek", backref="assigned_staff")

class Bookings(db.Model):
    __tablename__='bookings'
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trekker_id = db.Column(db.Integer, db.ForeignKey('trekker.trekker_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.trek_id'), nullable=False)
    booking_date = db.Column(db.Date, nullable = False)
    status = db.Column(db.Integer, nullable=False, default=0)  #0-booked, 1-cancelled, 2-completed
    payment_status = db.Column(db.Integer, nullable=False, default=0)  #0-pending, 1-paid, 2-refunded 
    
    