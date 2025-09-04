from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    access_level = db.Column(db.String(20), nullable=False, default='colaborador') # colaborador, tecnico, administrador
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets_created = db.relationship('Ticket', backref='author', lazy=True, foreign_keys='Ticket.user_id')
    tickets_assigned = db.relationship('Ticket', backref='assignee_user', lazy=True, foreign_keys='Ticket.assigned_to')
    comments = db.relationship('Comment', backref='comment_author', lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.sector}')"

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Quem abriu o chamado
    origin_sector = db.Column(db.String(50), nullable=False)
    target_sector = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='baixa') # baixa, media, alta
    status = db.Column(db.String(20), nullable=False, default='Aberto') # Aberto, Em Atendimento, Resolvido, Fechado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Quem está atendendo
    
    comments = db.relationship('Comment', backref='ticket', lazy=True, cascade="all, delete-orphan")
    history = db.relationship('TicketHistory', backref='ticket', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Ticket('{self.title}', '{self.status}', '{self.priority}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Comment('{self.content[:20]}...', 'Ticket ID: {self.ticket_id}')"

class TicketHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Usuário que fez a alteração
    field_changed = db.Column(db.String(50), nullable=False) # Ex: 'status', 'assigned_to', 'priority'
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    changed_by = db.relationship('User', backref='history_changes', lazy=True)

    def __repr__(self):
        return f"TicketHistory(Ticket:{self.ticket_id}, Field:{self.field_changed}, Old:{self.old_value}, New:{self.new_value})"