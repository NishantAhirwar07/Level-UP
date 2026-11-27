from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from datetime import date
from extensions import db
from models import Task
from routes import login_required

tasks_bp=Blueprint('tasks',__name__,url_prefix='/tasks')

@tasks_bp.route('/',methods=['GET','POST'])
@login_required
def index():
    uid=session['user_id']
    if request.method=='POST':
        title=request.form.get('title','').strip(); priority=request.form.get('priority','Medium'); due=request.form.get('due_date') or None
        if not title or len(title)>160 or priority not in ('Low','Medium','High'):
            flash('Enter a task title and valid priority.','danger')
        else:
            try:
                task=Task(user_id=uid,title=title,description=request.form.get('description','').strip(),due_date=date.fromisoformat(due) if due else None,priority=priority,category=request.form.get('category','General')[:50])
                db.session.add(task); db.session.commit(); flash('Task added.','success')
            except ValueError:
                db.session.rollback(); flash('Please provide a valid due date.','danger')
        return redirect(url_for('tasks.index'))
    status=request.args.get('status'); query=Task.query.filter_by(user_id=uid)
    if status in ('Pending','In Progress','Completed'): query=query.filter_by(status=status)
    items=query.order_by(Task.due_date.is_(None),Task.due_date,Task.created_at.desc()).all()
    return render_template('module.html',title='Tasks',kind='tasks',items=items)

@tasks_bp.post('/<int:item_id>/status')
@login_required
def status(item_id):
    item=Task.query.filter_by(id=item_id,user_id=session['user_id']).first_or_404(); value=request.form.get('status')
    if value not in ('Pending','In Progress','Completed'): abort(400)
    item.status=value; db.session.commit(); flash('Task status updated.','success'); return redirect(url_for('tasks.index'))

@tasks_bp.post('/<int:item_id>/delete')
@login_required
def delete(item_id):
    item=Task.query.filter_by(id=item_id,user_id=session['user_id']).first_or_404(); db.session.delete(item); db.session.commit(); flash('Task deleted.','success'); return redirect(url_for('tasks.index'))
