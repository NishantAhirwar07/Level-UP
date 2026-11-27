from flask import Blueprint, render_template, session, Response
from datetime import date
from sqlalchemy import func
from extensions import db
from models import Income, Expense, Task, HabitLog, Habit
from routes import login_required
import csv, io

reports_bp=Blueprint('reports',__name__,url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    uid=session['user_id']; year=str(date.today().year)
    rows=db.session.query(func.strftime('%Y-%m',Expense.transaction_date),func.sum(Expense.amount)).filter(Expense.user_id==uid,func.strftime('%Y',Expense.transaction_date)==year).group_by(func.strftime('%Y-%m',Expense.transaction_date)).all()
    categories=db.session.query(Expense.category,func.sum(Expense.amount)).filter_by(user_id=uid).group_by(Expense.category).all()
    income=db.session.query(func.coalesce(func.sum(Income.amount),0)).filter(Income.user_id==uid,func.strftime('%Y',Income.transaction_date)==year).scalar() or 0
    expense=db.session.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.user_id==uid,func.strftime('%Y',Expense.transaction_date)==year).scalar() or 0
    tasks=Task.query.filter_by(user_id=uid).all(); task_rate=round(sum(t.status=='Completed' for t in tasks)*100/len(tasks)) if tasks else 0
    habit_logs=HabitLog.query.join(Habit).filter(Habit.user_id==uid).all(); habit_rate=round(sum(x.completed for x in habit_logs)*100/len(habit_logs)) if habit_logs else 0
    return render_template('reports.html',month_labels=[x[0] for x in rows],month_values=[float(x[1]) for x in rows],category_labels=[x[0] for x in categories],category_values=[float(x[1]) for x in categories],income=income,expense=expense,savings=income-expense,task_rate=task_rate,habit_rate=habit_rate)

@reports_bp.route('/csv')
@login_required
def csv_export():
    uid=session['user_id']; output=io.StringIO(); writer=csv.writer(output); writer.writerow(['Type','Date','Category/Source','Amount','Description'])
    for row in Income.query.filter_by(user_id=uid).all(): writer.writerow(['Income',row.transaction_date,row.source,row.amount,row.description])
    for row in Expense.query.filter_by(user_id=uid).all(): writer.writerow(['Expense',row.transaction_date,row.category,row.amount,row.description])
    return Response(output.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=lifeflow-financial-report.csv'})
