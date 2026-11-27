from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from sqlalchemy import func
from datetime import date
from extensions import db
from models import User, Task, Habit, HabitLog, Income, Expense, Budget
from routes import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def landing():
    if session.get('user_id'):
        return redirect(url_for('dashboard.home'))
    return render_template('landing.html')


@dashboard_bp.route('/dashboard')
@login_required
def home():
    uid = session['user_id']
    today = date.today()
    month = today.strftime('%Y-%m')
    month_start = date(today.year, today.month, 1)
    next_month = date(today.year + (today.month == 12), 1 if today.month == 12 else today.month + 1, 1)

    # Date ranges work on both SQLite and PostgreSQL (unlike SQLite's strftime).
    month_income = Income.transaction_date >= month_start
    before_next_month_income = Income.transaction_date < next_month
    month_expense = Expense.transaction_date >= month_start
    before_next_month_expense = Expense.transaction_date < next_month

    income = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(
        Income.user_id == uid, month_income, before_next_month_income
    ).scalar() or 0
    expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.user_id == uid, month_expense, before_next_month_expense
    ).scalar() or 0
    budget = db.session.query(func.coalesce(func.sum(Budget.amount), 0)).filter(
        Budget.user_id == uid, Budget.month == month
    ).scalar() or 0

    tasks = Task.query.filter_by(user_id=uid).all()
    today_tasks = [task for task in tasks if task.due_date == today]
    completed = sum(task.status == 'Completed' for task in today_tasks)
    habits = Habit.query.filter_by(user_id=uid).all()
    habit_done = HabitLog.query.join(Habit).filter(
        Habit.user_id == uid,
        HabitLog.completion_date == today,
        HabitLog.completed.is_(True)
    ).count()
    recent = Expense.query.filter_by(user_id=uid).order_by(Expense.transaction_date.desc()).limit(5).all()
    chart_rows = db.session.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.user_id == uid, month_expense, before_next_month_expense
    ).group_by(Expense.category).all()

    return render_template(
        'dashboard.html',
        income=income,
        expense=expense,
        balance=income - expense,
        remaining=budget - expense,
        tasks=today_tasks,
        completed=completed,
        productivity=round(completed * 100 / len(today_tasks)) if today_tasks else 0,
        habits=habits,
        habit_done=habit_done,
        recent=recent,
        chart_labels=[row[0] for row in chart_rows],
        chart_values=[float(row[1]) for row in chart_rows]
    )


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.session.get(User, session['user_id'])
    if request.method == 'POST':
        name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        if not name or len(name) > 100 or '@' not in email:
            flash('Enter a valid name and email address.', 'danger')
        elif User.query.filter(User.email == email, User.id != user.id).first():
            flash('That email is already in use.', 'danger')
        else:
            user.full_name = name
            user.email = email
            db.session.commit()
            flash('Profile updated.', 'success')
        return redirect(url_for('dashboard.profile'))
    return render_template('profile.html', user=user)
