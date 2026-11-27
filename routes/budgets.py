from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date
from decimal import Decimal, InvalidOperation
from sqlalchemy import func
from extensions import db
from models import Budget, Expense
from routes import login_required

budgets_bp=Blueprint('budgets',__name__,url_prefix='/budgets')

@budgets_bp.route('/',methods=['GET','POST'])
@login_required
def index():
    uid=session['user_id']; month=date.today().strftime('%Y-%m')
    if request.method=='POST':
        category=request.form.get('category','All').strip()[:50] or 'All'
        try: amount=Decimal(request.form.get('amount','')).quantize(Decimal('0.01'))
        except (InvalidOperation,ValueError): amount=Decimal('0')
        budget_month=request.form.get('month',month)
        existing=Budget.query.filter_by(user_id=uid,month=budget_month,category=category).first()
        if amount<=0 or amount>Decimal('9999999999.99'): flash('Enter a positive budget amount.','danger')
        elif existing: existing.amount=amount; db.session.commit(); flash('Budget updated.','success')
        else: db.session.add(Budget(user_id=uid,month=budget_month,category=category,amount=amount)); db.session.commit(); flash('Budget created.','success')
        return redirect(url_for('budgets.index'))
    budgets=Budget.query.filter_by(user_id=uid).order_by(Budget.month.desc()).all(); spent={}
    for b in budgets:
        q=Expense.query.filter_by(user_id=uid).filter(func.strftime('%Y-%m',Expense.transaction_date)==b.month)
        if b.category!='All': q=q.filter_by(category=b.category)
        spent[b.id]=q.with_entities(func.coalesce(func.sum(Expense.amount),0)).scalar() or 0
    return render_template('module.html',title='Monthly Budgets',kind='budgets',items=budgets,spent=spent)

@budgets_bp.post('/<int:item_id>/delete')
@login_required
def delete(item_id):
    item=Budget.query.filter_by(id=item_id,user_id=session['user_id']).first_or_404(); db.session.delete(item); db.session.commit(); flash('Budget deleted.','success'); return redirect(url_for('budgets.index'))
