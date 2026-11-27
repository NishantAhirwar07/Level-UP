from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import or_
from werkzeug.security import generate_password_hash
from secrets import token_urlsafe
from extensions import db, limiter
from models import User
from routes import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('full_name','').strip(); uid=request.form.get('user_id','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password',''); confirm=request.form.get('confirm_password','')
        if len(name)>100 or not name or not uid.isalnum() or not 3<=len(uid)<=32 or '@' not in email or len(email)>254 or len(password)<10 or password!=confirm:
            flash('Check your details. Use a 3–32 character alphanumeric User ID and matching password of at least 10 characters.','danger')
        elif User.query.filter(or_(User.user_id==uid,User.email==email)).first():
            flash('That User ID or email is already registered.','danger')
        else:
            code=token_urlsafe(18); user=User(full_name=name,user_id=uid,email=email,recovery_hash=generate_password_hash(code)); user.set_password(password)
            db.session.add(user); db.session.commit(); return render_template('recovery_code.html',code=code)
    return render_template('auth_form.html',mode='register')

@auth_bp.route('/login', methods=['GET','POST'])
@limiter.limit('8 per minute')
def login():
    if request.method=='POST':
        identity=request.form.get('identity','').strip(); user=User.query.filter(or_(User.email==identity.lower(),User.user_id==identity)).first()
        if user and user.check_password(request.form.get('password','')):
            session.clear(); session['user_id']=user.id; session.permanent=True; return redirect(url_for('dashboard.home'))
        flash('Invalid credentials. Please try again.','danger')
    return render_template('auth_form.html',mode='login')

@auth_bp.post('/logout')
@login_required
def logout():
    session.clear(); flash('You are signed out.','success'); return redirect(url_for('dashboard.landing'))

@auth_bp.route('/forgot-user-id', methods=['GET','POST'])
@limiter.limit('5 per minute')
def forgot_id():
    found=None
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); code=request.form.get('recovery_code',''); user=User.query.filter_by(email=email).first()
        if user and user.check_recovery(code): found=user.user_id
        else: flash('Unable to verify those details.','danger')
    return render_template('auth_form.html',mode='forgot_id',found=found)

@auth_bp.route('/forgot-password', methods=['GET','POST'])
@limiter.limit('5 per minute')
def forgot_password():
    if request.method=='POST':
        identity=request.form.get('identity','').strip(); code=request.form.get('recovery_code',''); password=request.form.get('password',''); confirm=request.form.get('confirm_password','')
        user=User.query.filter(or_(User.email==identity.lower(),User.user_id==identity)).first()
        if user and user.check_recovery(code) and len(password)>=10 and password==confirm:
            user.set_password(password); new_code=token_urlsafe(18); user.recovery_hash=generate_password_hash(new_code); db.session.commit()
            return render_template('recovery_code.html',code=new_code)
        flash('Unable to verify those details or password.','danger')
    return render_template('auth_form.html',mode='forgot_password')

@auth_bp.post('/change-password')
@login_required
def change_password():
    user=db.session.get(User,session['user_id'])
    if not user.check_password(request.form.get('current_password','')) or len(request.form.get('new_password',''))<10 or request.form.get('new_password')!=request.form.get('confirm_password'):
        flash('Password could not be changed.','danger')
    else:
        user.set_password(request.form['new_password']); db.session.commit(); flash('Password updated.','success')
    return redirect(url_for('dashboard.profile'))
