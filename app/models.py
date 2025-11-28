from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    access_level = db.Column(db.String(20), nullable=False, default='colaborador')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    origin_sector = db.Column(db.String(50), nullable=False)
    target_sector = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='baixa')
    status = db.Column(db.String(20), nullable=False, default='Aberto')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True, default=None)
    
    attachment_filename = db.Column(db.String(100), nullable=True)
    
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
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
    attachment_filename = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Comment('{self.content[:20]}...', 'Ticket ID: {self.ticket_id}')"

class TicketHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    field_changed = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    changed_by = db.relationship('User', backref='history_changes', lazy=True)

    def __repr__(self):
        return f"TicketHistory(Ticket:{self.ticket_id}, Field:{self.field_changed}, Old:{self.old_value}, New:{self.new_value})"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
    ticket_link = db.relationship('Ticket', backref='related_notifications')

    def __repr__(self):
        return f"Notification('{self.message}', User: {self.user_id}, Read: {self.is_read})"

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    attachment_filename = db.Column(db.String(100), nullable=True)
    
    # --- CAMPO ADICIONADO PARA NOTIFICAÇÕES ---
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def __repr__(self):
        return f'<ChatMessage {self.sender_id} to {self.recipient_id}>'

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auto_close_days = db.Column(db.Integer, default=7)
    # --- CAMPO NOVO PARA LOGO ---
    logo_filename = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<SystemSettings {self.id}>'