from datetime import datetime
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
            staff = db.session.query(Staff).filter(Staff.user_id == user.user_id).first()
            if staff:
                if staff.status == 1:
                    return redirect(url_for('staff_dash'))
                elif staff.status == 0:
                    return ("Your account registration is still pending approval!")
                elif staff.status == 2:
                    return ("Your staff application has been rejected.")
                elif staff.status == 3:
                    return ("This account has been blacklisted. Access denied!")
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
            blacklisted_staff = db.session.query(Staff).filter(Staff.user_id == exists.user_id, Staff.status == 3).first()  
            if blacklisted_staff:
                return render_template("signup.html", error="This account has been blacklisted. Registration is not allowed.")
            return render_template("signup.html", error="Email is already registered!")
        else:
            #need to store in user_details
            ud = User_Details(email=uname, password=pwd,role=int(role))
            db.session.add(ud)
            db.session.commit() #save in the db
            #After user details, separate staff and trekker
            full_name=request.form.get("fname")
            address=request.form.get("address")
            phone_no=request.form.get("phno")
            if int(role)==2:
                user=Trekker(user_id=ud.user_id,full_name=full_name,address=address,phone_no=phone_no)
                db.session.add(user)
                db.session.commit()
                return redirect('/user_login')
            else:
                staff=Staff(user_id=ud.user_id,full_name=full_name,address=address,phone_no=phone_no)
                db.session.add(staff)
                db.session.commit()
                return redirect('/staff_login')
    else:
        return render_template("signup.html")
        

@app.route('/admin')
def admin_dash():
    total_treks = Trek.query.filter(Trek.status != 4).count()
    total_users = Trekker.query.filter_by(status=0).count()
    total_staff = Staff.query.filter_by(status=1).count()
    total_bookings = Bookings.query.count()

    recent_bookings = Bookings.query.order_by(Bookings.booking_id.desc()).limit(3).all()
    return render_template("admin_dash.html", total_treks=total_treks,total_users=total_users,total_staff=total_staff,total_bookings=total_bookings,recent_bookings=recent_bookings)

@app.route('/staff')
def staff_dash():
    return render_template("staff_dash.html")

@app.route('/user')
def user_dash():
    return render_template("user_dash.html")

@app.route('/manage_treks', methods=['GET'])
def manage_treks():
    removed_id = request.args.get('removed_id')
    if removed_id:
        trek = Trek.query.get_or_404(removed_id)
        trek.status = 4     
        db.session.commit()
        return redirect(url_for('manage_treks'))

    restore_id = request.args.get('restore_id')
    if restore_id:
        trek = Trek.query.get_or_404(restore_id)
        trek.status = 0  
        db.session.commit()
        return redirect(url_for('manage_treks'))
    recent_treks = Trek.query.filter(Trek.status.in_([0, 1, 2])).all()
    history_treks = Trek.query.filter(Trek.status.in_([3, 4])).all()
    return render_template("manage_treks.html", recent_treks=recent_treks, history_treks=history_treks)




@app.route('/manage_staff', methods=['GET', 'POST'])
def manage_staff():
    staff_id = request.args.get('staff_id')
    action = request.args.get('action') 

    if staff_id and action:        
        staff = Staff.query.get_or_404(staff_id)
        
        if action == 'approve':
            staff.status = 1
        elif action == 'reject':
            staff.status = 2
        elif action == 'blacklist':
            staff.status = 3
        elif action == 'undo':
                    staff.status = 0   
        db.session.commit()
        return redirect(url_for('manage_staff'))

    pending_staff = db.session.query(Staff).filter(Staff.status == 0).all()
    history_staff = db.session.query(Staff).filter(Staff.status != 0).all()

    return render_template("manage_staff.html", pending_staff=pending_staff, history_staff=history_staff)




@app.route('/manage_users', methods=['GET'])
def manage_users():
    action = request.args.get('action')
    trekker_id = request.args.get('trekker_id')

    if action and trekker_id:
        trekker = Trekker.query.get_or_404(trekker_id)
        
        if trekker:
            if action == 'deactivate':
                trekker.status = 1
            elif action == 'blacklist':
                trekker.status = 2 
            elif action == 'undo':
                trekker.status = 0  # Revert back to active status
                
            db.session.commit()
        return redirect(url_for('manage_users'))
    active_trekkers = db.session.query(Trekker).filter(Trekker.status == 0).all()
    history_trekkers = db.session.query(Trekker).filter(Trekker.status != 0).all()
    return render_template('manage_users.html', active_trekkers=active_trekkers, history_trekkers=history_trekkers)



@app.route('/bookings', methods=['GET'])
def manage_bookings():
    active_bookings = Bookings.query.filter(Bookings.status == 0).all()
    history_bookings = Bookings.query.filter(Bookings.status.in_([1, 2])).all()
    return render_template("manage_bookings.html", active_bookings=active_bookings, history_bookings=history_bookings)



@app.route('/add_trek', methods=['GET', 'POST'])
def add_trek():
    if request.method == 'POST':
        trek_name = request.form.get('trek_name')
        location = request.form.get('locn')
        difficulty = int(request.form.get('diff'))
        duration = int(request.form.get('durn'))
        av_slots = int(request.form.get('av_slots'))
        st_date = datetime.strptime(request.form.get('st_date'), '%Y-%m-%d').date()
        en_date = datetime.strptime(request.form.get('en_date'), '%Y-%m-%d').date()
        staff_assigned = int(request.form.get('staff_id'))
        status = int(request.form.get('status'))
        description = request.form.get('desn')

        new_trek = Trek(trek_name=trek_name, location=location, difficulty=difficulty, duration=duration, av_slots=av_slots,
                st_date=st_date, en_date=en_date, staff_assigned=staff_assigned, status=status, description=description)
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('manage_treks'))
    staff_list = Staff.query.filter(Staff.status == 1).all()
    return render_template('add_trek.html', staff_list=staff_list)
 




@app.route('/edit_trek/<int:trek_id>')
def edit_trek(trek_id):
    trek_data = Trek.query.get_or_404(trek_id)
    staff_list = Staff.query.filter_by(status=1).all()
    return render_template("edit_trek.html", trek_data=trek_data, staff_list=staff_list)

@app.route('/update_trek', methods=["GET","POST"])
def update_trek():
    trek_id = request.form.get("trek_id")
    old_trek_details = Trek.query.get_or_404(trek_id)

    old_trek_details.trek_name = request.form.get("trek_name")
    old_trek_details.location = request.form.get("locn")
    old_trek_details.description = request.form.get("desn")

    old_trek_details.difficulty = int(request.form.get("diff")) if request.form.get("diff") else None
    old_trek_details.duration = int(request.form.get("durn")) if request.form.get("durn") else None
    old_trek_details.av_slots = int(request.form.get("av_slots")) if request.form.get("av_slots") else None
    old_trek_details.status = int(request.form.get("status")) if request.form.get("status") else None

    select_staff = request.form.get("select_staff")
    if select_staff and select_staff.strip() and select_staff != "None":
      old_trek_details.staff_assigned = int(select_staff)
   
    st_date = request.form.get("st_date")
    en_date = request.form.get("en_date")
    
    if st_date:
        old_trek_details.st_date = datetime.strptime(st_date, "%Y-%m-%d").date()
    if en_date:
        old_trek_details.en_date = datetime.strptime(en_date, "%Y-%m-%d").date()
   
    db.session.commit()
    return redirect(url_for("manage_treks"))


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        pattern = f'%{query}%'
        for model in [User_Details, Staff, Trekker, Bookings, Trek]:
            mapper = db.inspect(model)
            filters = [db.cast(col, db.String).ilike(pattern) for col in mapper.columns]
            if filters:
              matches = model.query.filter(db.or_(*filters)).all()
              results.extend(matches)
    return render_template('results.html', query=query, results=results, getattr=getattr)






#additional python functions


def get_all_users():
    user_data=db.session.query(Trekker).filter().all()
    return user_data

def get_trek(trek_id):
    trek_data = db.session.query(Trek).filter(Trek.trek_id==trek_id).first()
    return trek_data


@app.route('/user_treks')
def user_treks():
    # Strictly OPEN treks that can be booked
    open_treks = Trek.query.filter_by(status=1).all()
    return render_template("user_treks.html", treks=open_treks)

@app.route('/staff_dashboard')
def staff_dashboard():
    # Visible to staff: Pending (0), Open (1), Closed (2), Completed (3)
    staff_treks = Trek.query.filter(Trek.status.in_([0, 1, 2, 3])).all()
    return render_template("staff_dashboard.html", treks=staff_treks)