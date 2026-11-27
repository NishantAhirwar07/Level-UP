from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from datetime import date
from decimal import Decimal, InvalidOperation
from extensions import db
from models import Income, Expense
from routes import login_required

finance_bp=Blueprint('finance',__name__,url_prefix='/finance')

@finance_bp.route('/<kind>',methods=['GET','POST'])
@login_required
def ledger(kind):
    if kind not in ('income','expenses'): abort(404)
    model=Income if kind=='income' else Expense; uid=session['user_id']
    if request.method=='POST':
        label=request.form.get('source' if kind=='income' else 'category','').strip()
        try: amount=Decimal(request.form.get('amount','')).quantize(Decimal('0.01'))
        except (InvalidOperation,ValueError): amount=Decimal('0')
        try: trans_date=date.fromisoformat(request.form.get('transaction_date') or date.today().isoformat())
        except ValueError: trans_date=None
        if not label or amount<=0 or amount>Decimal('9999999999.99') or not trans_date:
            flash('Provide a valid category/source, date and positive amount.','danger')
        else:
            fields={'user_id':uid,'amount':amount,'transaction_date':trans_date,'description':request.form.get('description','').strip()[:250]}
            if kind=='income': fields['source']=label[:50]
            else: fields.update(category=label[:50],payment_method=request.form.get('payment_method','Other')[:40])
            db.session.add(model(**fields)); db.session.commit(); flash('Transaction saved.','success')
        return redirect(url_for('finance.ledger',kind=kind))
    items=model.query.filter_by(user_id=uid).order_by(model.transaction_date.desc(),model.id.desc()).limit(100).all()
    return render_template('module.html',title='Income' if kind=='income' else 'Expenses',kind=kind,items=items)

@finance_bp.post('/<kind>/<int:item_id>/delete')
@login_required
def delete(kind,item_id):
    if kind not in ('income','expenses'): abort(404)
    model=Income if kind=='income' else Expense
    item=model.query.filter_by(id=item_id,user_id=session['user_id']).first_or_404(); db.session.delete(item); db.session.commit(); flash('Transaction deleted.','success'); return redirect(url_for('finance.ledger',kind=kind))
