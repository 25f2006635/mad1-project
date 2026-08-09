from datetime import datetime, date
from flask import render_template, request, redirect, url_for, session
from flask import current_app as app
from models import *
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import cast, String, or_


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
            login_user(user)
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
                    login_user(user)
                    session['user_id'] = user.user_id
                    session['staff_id'] = staff.staff_id
                    return redirect(url_for('staff_dash'))
                elif staff.status == 0:
                    return ("Your account registration is still pending approval!")
                elif staff.status == 2:
                    return ("Your staff application has been rejected. Try again next time with different mail-id.")
                elif staff.status == 3:
                    return ("This account has been blacklisted. Access denied!")
            else:
                return ("Staff profile not found!")
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
            trekker = db.session.query(Trekker).filter(Trekker.user_id == user.user_id).first()
            if trekker:
                if trekker.status != 2:
                    login_user(user)
                    session['user_id'] = user.user_id
                    session['trekker_id'] = trekker.trekker_id
                    return redirect(url_for('user_dash'))
                elif trekker.status == 2:
                    return ("This account has been blacklisted. Access denied!")
            else:
                return ("Trekker profile not found!")
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
@login_required
def admin_dash():
    total_treks = Trek.query.filter(Trek.status != 4).count()
    total_users = Trekker.query.filter(Trekker.status != 2).count()
    total_staff = Staff.query.filter_by(status=1).count()
    total_bookings = Bookings.query.count()

    recent_bookings = Bookings.query.order_by(Bookings.booking_id.desc()).limit(3).all()
    return render_template("admin_dash.html", total_treks=total_treks,total_users=total_users,total_staff=total_staff,total_bookings=total_bookings,recent_bookings=recent_bookings)



@app.route('/manage_treks', methods=['GET'])
@login_required
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
@login_required
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
@login_required
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
    active_trekkers = db.session.query(Trekker).filter(Trekker.status != 2).all()
    history_trekkers = db.session.query(Trekker).filter(Trekker.status == 2).all()
    return render_template('manage_users.html', active_trekkers=active_trekkers, history_trekkers=history_trekkers)


@app.route('/bookings', methods=['GET'])
@login_required
def manage_bookings():
    active_bookings = Bookings.query.filter(Bookings.status == 0).all()
    history_bookings = Bookings.query.filter(Bookings.status.in_([1, 2])).all()
    return render_template("manage_bookings.html", active_bookings=active_bookings, history_bookings=history_bookings)


@app.route('/add_trek', methods=['GET', 'POST'])
@login_required
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
@login_required
def edit_trek(trek_id):
    trek_data = Trek.query.get_or_404(trek_id)
    staff_list = Staff.query.filter_by(status=1).all()
    return render_template("edit_trek.html", trek_data=trek_data, staff_list=staff_list)


@app.route('/update_trek', methods=["GET","POST"])
@login_required
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


@app.route('/staff_dash')
@login_required
def staff_dash():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('staff_signin'))

    staff = db.session.query(Staff).filter(Staff.user_id == user_id).first()
    if not staff:
        return redirect(url_for('staff_signin'))
    

    assigned_treks_query = Trek.query.filter(Trek.assigned_staff == staff, Trek.status.in_([0, 1, 2, 3]))
    total_treks = assigned_treks_query.count()
    assigned_treks = assigned_treks_query.limit(3).all()
    open_treks = Trek.query.filter(Trek.assigned_staff == staff, Trek.status == 1).count()
    trek_ids = [trek.trek_id for trek in assigned_treks]
    total_participants = db.session.query(Bookings).filter(Bookings.trek_id.in_(trek_ids)).count() if trek_ids else 0
   
    return render_template("staff_dash.html", treks=assigned_treks, total_treks=total_treks, total_participants=total_participants, open_treks=open_treks, staff=staff)



def get_current_staff():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return Staff.query.filter_by(user_id=user_id).first()


@app.route('/staff_manage_treks', methods=['GET', 'POST'])
@login_required
def staff_manage_treks():
    staff = get_current_staff()
    if not staff:
        return redirect(url_for('staff_signin'))

    treks = Trek.query.filter_by(assigned_staff=staff).all()
    trek_ids = [t.trek_id for t in treks]
    bookings = Bookings.query.filter(Bookings.trek_id.in_(trek_ids)).all() if trek_ids else []
    participant_count = len(bookings)

    if request.method == 'POST':
        # Handle inline updates if editing directly from the main list page
        trek_id = request.form.get('trek_id', type=int)
        trek = Trek.query.filter_by(trek_id=trek_id, assigned_staff=staff).first_or_404()

        action = request.form.get('action')
        if action == 'mark_started':
            trek.status = 1  # Open/Started
        elif action == 'mark_completed':
            trek.status = 3  # Completed
        elif 'av_slots' in request.form:
            trek.av_slots = request.form.get('av_slots')
            if 'status' in request.form:
                trek.status = int(request.form.get('status'))

        db.session.commit()
        return redirect(url_for('staff_manage_treks'))
    return render_template('staff_manage_treks.html', treks=treks, bookings=bookings, participant_count=participant_count, staff=staff)


@app.route('/staff_edit_trek/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def staff_edit_trek(trek_id):
    staff = get_current_staff()
    if not staff:
        return redirect(url_for('staff_signin'))
    trek = Trek.query.filter_by(trek_id=trek_id, assigned_staff=staff).first_or_404()
    if request.method == 'POST':
        trek.av_slots = request.form.get('av_slots', type=int)
        trek.status = request.form.get('status', type=int)
        db.session.commit()
        return redirect(url_for('staff_manage_treks'))

    return render_template('staff_edit_trek.html', staff=staff, trek=trek)


@app.route('/staff_participants')
@login_required
def staff_participants():
    staff = get_current_staff()
    if not staff:
        return redirect(url_for('staff_signin'))

    assigned_treks = Trek.query.filter_by(assigned_staff=staff).all()
    selected_trek_id = request.args.get('trek_id', type=int)

    if not selected_trek_id and assigned_treks:
        selected_trek_id = assigned_treks[0].trek_id

    bookings = []
    if selected_trek_id:
        trek = Trek.query.filter_by(trek_id=selected_trek_id, assigned_staff=staff).first_or_404()
        bookings = Bookings.query.filter_by(trek_id=trek.trek_id).all()

    return render_template('staff_participants.html', staff=staff, assigned_treks=assigned_treks, selected_trek_id=selected_trek_id, bookings=bookings)


@app.route('/staff_profile', methods=['GET', 'POST'])
@login_required
def staff_profile():
    staff = get_current_staff()
    if not staff:
        return redirect(url_for('staff_signin'))

    return render_template('staff_profile.html', staff=staff)


@app.route('/staff_edit_profile', methods=['GET', 'POST'])
@login_required
def staff_edit_profile():
    staff = get_current_staff()
    if not staff:
        return redirect(url_for('staff_signin'))
    
    if request.method == 'POST':
            # Permission Rule: View/Update phone, address, and password
        staff.phone = request.form.get('phone')
        staff.address = request.form.get('address')
            
        db.session.commit()
        return redirect(url_for('staff_profile'))
    
    return render_template('staff_edit_profile.html', staff=staff)



@app.route('/user')
@login_required
def user_dash():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))

    trekker = Trekker.query.filter_by(user_id=user_id).first()
    if not trekker:
        return redirect(url_for('user_signin'))

    booked_trek_ids = [b.trek_id for b in Bookings.query.filter_by(trekker_id=trekker.trekker_id).filter(Bookings.status != 1).all()]
    all_active_treks = Trek.query.filter(Trek.status == 1, Trek.av_slots > 0)
    unbooked_treks = [t for t in all_active_treks if t.trek_id not in booked_trek_ids]
    available_treks_count = len(unbooked_treks)
    available_treks = unbooked_treks[:3]

    my_bookings_count = Bookings.query.join(Trek).filter(
        Bookings.trekker_id == trekker.trekker_id,
        Bookings.status == 0,
        Trek.status == 1
    ).count()
    completed_treks_count = Bookings.query.join(Trek).filter(
        Bookings.trekker_id == trekker.trekker_id,
        (Bookings.status == 2) | (Trek.status == 3)
    ).count()
   
    return render_template("user_dash.html", user_name=trekker.full_name, available_treks_count=available_treks_count,
        my_bookings_count=my_bookings_count, completed_treks_count=completed_treks_count, available_treks=available_treks)


@app.route('/browse_treks')
@login_required
def browse_treks():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))

    trekker = Trekker.query.filter_by(user_id=user_id).first()
    if not trekker:
        return redirect(url_for('user_signin'))

    selected_loc = request.args.get('locn', 'All')
    selected_diff = request.args.get('diff', 'All')

    # Get active booked trek IDs
    booked_trek_ids = [
        b.trek_id for b in Bookings.query.filter_by(trekker_id=trekker.trekker_id).filter(Bookings.status != 1).all()
    ]

    query = Trek.query.filter(Trek.status == 1)

    if booked_trek_ids:
        query = query.filter(~Trek.trek_id.in_(booked_trek_ids))

    all_open = query.all()
    locations = sorted(list({t.location for t in all_open if t.location}))

    if selected_loc and 'All' not in selected_loc:
        query = query.filter(Trek.location == selected_loc)

    if selected_diff and 'All' not in selected_diff:
        diff_map = {
            '0': ['Easy', 0, '0'],
            '1': ['Moderate', 1, '1'],
            '2': ['Hard', 2, '2'],
            'Easy': ['Easy', 0, '0'],
            'Moderate': ['Moderate', 1, '1'],
            'Hard': ['Hard', 2, '2']
        }
        if selected_diff in diff_map:
            query = query.filter(Trek.difficulty.in_(diff_map[selected_diff]))
        else:
            query = query.filter(Trek.difficulty == selected_diff)

    available_treks = query.all()

    return render_template(
        "user_browse_treks.html",
        user_name=trekker.full_name,
        available_treks=available_treks,
        locations=locations,
        selected_loc=selected_loc,
        selected_diff=selected_diff,
        booked_trek_ids=booked_trek_ids
    )

@app.route('/book_trek/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))

    trekker = Trekker.query.filter_by(user_id=user_id).first()
    if not trekker:
        return redirect(url_for('user_signin'))
    existing_booking = Bookings.query.filter_by(trekker_id=trekker.trekker_id, trek_id=trek_id).filter(Bookings.status != 1).first()
    if existing_booking:
        return redirect(url_for('my_bookings'))

    trek = Trek.query.get_or_404(trek_id)

    if trek.status == 1 and trek.av_slots > 0:
        trek.av_slots -= 1

        new_booking = Bookings(trekker_id=trekker.trekker_id, trek_id=trek_id, booking_date=date.today(), status=0, payment_status=0)

        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('my_bookings'))
    return redirect(url_for('browse_treks', user_name=trekker.full_name))


@app.route('/my_bookings')
@login_required
def my_bookings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))

    trekker = Trekker.query.filter_by(user_id=user_id).first()
    if not trekker:
        return redirect(url_for('user_signin'))
    active_bookings = Bookings.query.join(Trek).filter(
        Bookings.trekker_id == trekker.trekker_id,
        Bookings.status == 0,
        Trek.status == 1
    ).all()
    return render_template('user_bookings.html', user_name=trekker.full_name, user_bookings=active_bookings)


@app.route('/booking_details/<int:booking_id>')
@login_required
def booking_details(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))
    booking = Bookings.query.get_or_404(booking_id)
    return render_template("user_booking_details.html",user_name=booking.trekker.full_name,  booking=booking)


@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))
    booking = Bookings.query.get_or_404(booking_id)
    trek = Trek.query.get_or_404(booking.trek_id)
    if booking.status == 0:
        booking.status = 1
        trek.av_slots += 1

        db.session.commit()
    return redirect(url_for('my_bookings', user_name=booking.trekker.full_name, booking_id=booking_id))


@app.route('/my_history')
@login_required
def my_history():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))
    trekker = Trekker.query.filter_by(user_id=user_id).first()
    if not trekker:
        return redirect(url_for('user_signin'))
    history_bookings = Bookings.query.join(Trek).filter(
        Bookings.trekker_id == trekker.trekker_id,
        (Bookings.status != 0) | (Trek.status != 1)
    ).all()
    return render_template("user_history.html", user_name=trekker.full_name, bookings=history_bookings)

@app.route('/my_profile')
@login_required
def my_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))
    trekker = Trekker.query.filter_by(user_id=user_id).first()
    return render_template("user_profile.html", user_name=trekker.full_name, trekker=trekker)


@app.route('/user_edit_profile', methods=['GET', 'POST'])
@login_required
def user_edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_signin'))

    trekker = Trekker.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        trekker.full_name = request.form.get('name')
        trekker.phone_no = request.form.get('phone')
        trekker.address = request.form.get('address')

        if trekker.status != 2:
            new_status = request.form.get('status')
            if new_status in ['0', '1']:
                trekker.status = int(new_status)
        db.session.commit()
        return redirect(url_for('my_profile'))

    return render_template('user_edit_profile.html', trekker=trekker, user_name=trekker.full_name)



@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()

    results = {'treks': [],'staff': [], 'users': [], 'bookings': []}
    if not query:
        return render_template('results.html', results=results, query=query)

    pattern = f"%{query}%"
    role = current_user.role

    if role == 0:
        results['treks'] = Trek.query.filter(db.or_(Trek.trek_name.ilike(pattern),cast(Trek.trek_id, String).ilike(pattern))).all()
        results['staff'] = Staff.query.filter(db.or_(Staff.full_name.ilike(pattern), cast(Staff.staff_id, String).ilike(pattern))).all()
        results['users'] = User_Details.query.outerjoin(Trekker).filter(db.or_(User_Details.email.ilike(pattern),cast(User_Details.user_id, String).ilike(pattern),Trekker.full_name.ilike(pattern))).all()
        results['bookings'] = Bookings.query.filter(cast(Bookings.booking_id, String).ilike(pattern)).all()
    elif role == 1 :
        staff_record = current_user.staff
        if staff_record:
            results['treks'] = Trek.query.filter(Trek.staff_assigned == staff_record.staff_id,db.or_(Trek.trek_name.ilike(pattern),cast(Trek.trek_id, String).ilike(pattern))).all()
            results['bookings'] = Bookings.query.join(Trek).join(Trekker).filter(Trek.staff_assigned == staff_record.staff_id,db.or_(cast(Bookings.booking_id, String).ilike(pattern),Trekker.full_name.ilike(pattern))).all()
    else:
        results['treks'] = Trek.query.filter(
            Trek.status == 0, db.or_( Trek.trek_name.ilike(pattern),Trek.location.ilike(pattern))).all()
        
    return render_template('results.html', query=query, results=results)


@app.route('/update_payment_status/<int:booking_id>', methods=['POST'])
@login_required
def update_payment_status(booking_id):
    booking = Bookings.query.get_or_404(booking_id)
    
    new_status = request.form.get('payment_status', type=int)
    
    if new_status is not None and new_status in [0, 1, 2]:
        booking.payment_status = new_status
        db.session.commit()
        
    return redirect(request.referrer or url_for('admin_dash'))


@app.route('/admin_logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_signin'))

@app.route('/staff_logout')
def staff_logout():
    logout_user()
    return redirect(url_for('staff_signin'))

@app.route('/user_logout')
def user_logout():
    logout_user()
    return redirect(url_for('user_signin'))