from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)  # ← EKLENDİ
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='agent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets = db.relationship('Ticket', backref='assigned_user', lazy=True)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(128), nullable=False)
    contact_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64))
    priority = db.Column(db.String(16))
    status = db.Column(db.String(32), default="Bekliyor")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

class TicketLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.Text)

    user = db.relationship('User')
    ticket = db.relationship('Ticket')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_comment_user_id'), nullable=False)

    user = db.relationship('User', backref='comments')
    ticket = db.relationship('Ticket', backref='comments')


