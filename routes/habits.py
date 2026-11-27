from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date, timedelta
from extensions import db
from models import Habit, HabitLog
from routes import login_required

habits_bp=Blueprint('habits',__name__,url_prefix='/habits')

@habits_bp.route('/',methods=['GET','POST'])
@login_required
def index():
    uid=session['user_id']; today=date.today()
    if request.method=='POST':
        name=request.form.get('name','').strip()
        if not name or len(name)>100: flash('Habit name is required.','danger')
        else:
            db.session.add(Habit(user_id=uid,name=name,description=request.form.get('description','').strip()[:250],routine_time=request.form.get('routine_time','08:00'))); db.session.commit(); flash('Habit added.','success')
        return redirect(url_for('habits.index'))
    habits=Habit.query.filter_by(user_id=uid).order_by(Habit.routine_time).all(); logs={l.habit_id:l for l in HabitLog.query.join(Habit).filter(Habit.user_id==uid,HabitLog.completion_date==today).all()}
    week_start=today-timedelta(days=today.weekday()); weekly=HabitLog.query.join(Habit).filter(Habit.user_id==uid,HabitLog.completion_date>=week_start,HabitLog.completion_date<=today,HabitLog.completed.is_(True)).count()
    return render_template('module.html',title='Habits & Routine',kind='habits',items=habits,logs=logs,weekly=weekly)

@habits_bp.post('/<int:habit_id>/log')
@login_required
def log(habit_id):
    habit=Habit.query.filter_by(id=habit_id,user_id=session['user_id']).first_or_404(); today=date.today(); entry=HabitLog.query.filter_by(habit_id=habit.id,completion_date=today).first()
    if entry is None: entry=HabitLog(habit_id=habit.id,completion_date=today); db.session.add(entry)
    entry.completed=request.form.get('completed')=='1'; db.session.commit(); flash('Today’s habit log saved.','success'); return redirect(url_for('habits.index'))

@habits_bp.post('/<int:habit_id>/delete')
@login_required
def delete(habit_id):
    item=Habit.query.filter_by(id=habit_id,user_id=session['user_id']).first_or_404(); db.session.delete(item); db.session.commit(); flash('Habit deleted.','success'); return redirect(url_for('habits.index'))
