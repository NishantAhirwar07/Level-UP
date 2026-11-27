from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    recovery_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tasks = db.relationship('Task', backref='owner', cascade='all, delete-orphan')
    habits = db.relationship('Habit', backref='owner', cascade='all, delete-orphan')
    incomes = db.relationship('Income', backref='owner', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='owner', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='owner', cascade='all, delete-orphan')

    def set_password(self, value): self.password_hash = generate_password_hash(value)
    def check_password(self, value): return check_password_hash(self.password_hash, value)
    def check_recovery(self, value): return check_password_hash(self.recovery_hash, value)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, default='')
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(12), default='Medium', nullable=False)
    status = db.Column(db.String(16), default='Pending', nullable=False)
    category = db.Column(db.String(50), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), default='')
    routine_time = db.Column(db.String(5), default='08:00')
    logs = db.relationship('HabitLog', backref='habit', cascade='all, delete-orphan')

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id', ondelete='CASCADE'), nullable=False)
    completion_date = db.Column(db.Date, nullable=False, default=date.today)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    __table_args__ = (db.UniqueConstraint('habit_id', 'completion_date', name='uq_habit_day'),)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(250), default='')

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(db.String(40), default='Other')
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(250), default='')

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    month = db.Column(db.String(7), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='All')
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'month', 'category', name='uq_user_month_category'),)
