import os
import uuid
import shutil
from werkzeug.utils import secure_filename
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, Blueprint, current_app, send_from_directory, session, Response
from app import db
from app.forms import LoginForm, RegistrationForm, TicketForm, CommentForm, TicketUpdateForm, ChangePasswordForm, ChatMessageForm, SettingsForm
from app.models import User, Ticket, Comment, TicketHistory, ChatMessage, SystemSettings
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, or_, cast, String, not_, and_
import json
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

# --- CONTEXT PROCESSOR (Disponibiliza configurações globais nos templates) ---
@main.context_processor
def inject_system_settings():
    settings = SystemSettings.query.first()
    return dict(system_settings=settings)

# --- FUNÇÕES AUXILIARES ---
def save_attachment(form_attachment):
    if not form_attachment or not form_attachment.filename:
        return None
    random_hex = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_attachment.filename)
    secure_name = secure_filename(f"{random_hex}{f_ext}")
    upload_path = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, secure_name)
    form_attachment.save(file_path)
    return secure_name

def save_chat_attachment(form_attachment):
    if not form_attachment or not form_attachment.filename:
        return None
    random_hex = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_attachment.filename)
    secure_name = secure_filename(f"{random_hex}{f_ext}")
    upload_path = os.path.join(current_app.static_folder, 'chat_uploads')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, secure_name)
    form_attachment.save(file_path)
    return secure_name

# --- NOVA FUNÇÃO PARA SALVAR LOGO ---
def save_logo(form_logo):
    if not form_logo or not form_logo.filename:
        return None
    random_hex = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_logo.filename)
    secure_name = secure_filename(f"logo_{random_hex}{f_ext}")
    # Salva na pasta padrão de uploads
    upload_path = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, secure_name)
    form_logo.save(file_path)
    return secure_name

def is_admin():
    return current_user.is_authenticated and current_user.access_level == 'administrador'

def is_tecnico():
    return current_user.is_authenticated and (current_user.access_level == 'tecnico' or current_user.access_level == 'administrador')

# --- ROTAS PRINCIPAIS E DE USUÁRIOS ---
@main.route('/')
@main.route('/home')
@login_required
def home():
    session.pop('last_check_time', None)
    query_param = request.args.get('q', '', type=str)
    
    if current_user.access_level == 'administrador':
        base_query = Ticket.query
    elif current_user.access_level == 'tecnico':
        base_query = Ticket.query.filter(or_(Ticket.target_sector == current_user.sector, Ticket.origin_sector == current_user.sector, Ticket.assigned_to == current_user.id))
    else:
        base_query = Ticket.query.filter_by(user_id=current_user.id)

    if query_param:
        search_term = f"%{query_param}%"
        base_query = base_query.filter(or_(Ticket.title.ilike(search_term), cast(Ticket.id, String).ilike(search_term)))
    else:
        base_query = base_query.filter(not_(Ticket.status.in_(['Resolvido', 'Fechado'])))

    tickets = base_query.order_by(Ticket.created_at.desc()).all()
    return render_template('index.html', title='Início', tickets=tickets)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.is_active:
                login_user(user)
                next_page = request.args.get('next')
                flash(f'Bem-vindo, {user.name}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Sua conta está bloqueada. Por favor, contate o administrador.', 'danger')
        else:
            flash('Login sem sucesso. Por favor, verifique seu e-mail e senha.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not is_admin():
        abort(403)
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(name=form.name.data, email=form.email.data, sector=form.sector.data, password=hashed_password, access_level=form.access_level.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Conta criada para {form.name.data}!', 'success')
        return redirect(url_for('main.user_management'))
    return render_template('register.html', title='Cadastrar Usuário', form=form)

# --- ROTAS DE CHAMADOS ---
@main.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        attachment_filename = save_attachment(form.attachment.data)
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id,
            origin_sector=form.origin_sector.data,
            target_sector=form.target_sector.data,
            priority=form.priority.data,
            attachment_filename=attachment_filename
        )
        db.session.add(ticket)
        db.session.commit()
        history_entry = TicketHistory(ticket_id=ticket.id, changed_by_user_id=current_user.id, field_changed='status', old_value='N/A', new_value='Aberto')
        db.session.add(history_entry)
        db.session.commit()
        flash('Seu chamado foi aberto com sucesso!', 'success')
        return redirect(url_for('main.tickets_kanban'))
    form.origin_sector.data = current_user.sector
    return render_template('create_ticket.html', title='Abrir Chamado', form=form)

@main.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not (current_user.id == ticket.user_id or (is_tecnico() and (ticket.target_sector == current_user.sector or ticket.origin_sector == current_user.sector)) or is_admin()):
        abort(403)
    comment_form = CommentForm()
    update_form = TicketUpdateForm()
    if is_tecnico():
        tecnicos = User.query.filter(or_(User.access_level == 'tecnico', User.access_level == 'administrador')).all()
        update_form.assigned_to.choices = [(0, 'Não Atribuído')] + [(t.id, f"{t.name} ({t.sector})") for t in tecnicos]
    if request.method == 'POST':
        if update_form.submit_update.data and update_form.validate():
            new_status = update_form.status.data
            if new_status == 'Fechado' and ticket.status != 'Fechado':
                ticket.closed_at = datetime.utcnow()
            elif new_status != 'Fechado' and ticket.status == 'Fechado':
                ticket.closed_at = None
            changes = []
            if update_form.status.data != ticket.status:
                changes.append(('status', ticket.status, update_form.status.data))
                ticket.status = update_form.status.data
            if update_form.priority.data != ticket.priority:
                changes.append(('priority', ticket.priority, update_form.priority.data))
                ticket.priority = update_form.priority.data
            new_assigned_to = update_form.assigned_to.data if update_form.assigned_to.data != 0 else None
            if new_assigned_to != ticket.assigned_to:
                old_assignee = User.query.get(ticket.assigned_to)
                new_assignee = User.query.get(new_assigned_to)
                old_assignee_name = old_assignee.name if old_assignee else 'N/A'
                new_assignee_name = new_assignee.name if new_assignee else 'N/A'
                changes.append(('assigned_to', old_assignee_name, new_assignee_name))
                ticket.assigned_to = new_assigned_to
            for field, old_val, new_val in changes:
                history_entry = TicketHistory(ticket_id=ticket.id, changed_by_user_id=current_user.id, field_changed=field, old_value=old_val, new_value=new_val)
                db.session.add(history_entry)
            db.session.commit()
            flash('Chamado atualizado com sucesso!', 'success')
            return redirect(url_for('main.view_ticket', ticket_id=ticket.id))
        if comment_form.submit_comment.data and comment_form.validate():
            attachment_filename = save_attachment(comment_form.attachment.data)
            comment = Comment(content=comment_form.content.data, 
                              user_id=current_user.id, 
                              ticket_id=ticket.id,
                              attachment_filename=attachment_filename)
            db.session.add(comment)
            db.session.commit()
            flash('Comentário adicionado!', 'success')
            return redirect(url_for('main.view_ticket', ticket_id=ticket.id))
    if request.method == 'GET' and is_tecnico():
        update_form.status.data = ticket.status
        update_form.priority.data = ticket.priority
        update_form.assigned_to.data = ticket.assigned_to or 0
    return render_template('view_ticket.html', title=ticket.title, ticket=ticket, comment_form=comment_form, update_form=update_form, is_tecnico=is_tecnico(), is_admin=is_admin())

@main.route('/tickets_kanban')
@login_required
def tickets_kanban():
    session.pop('last_check_time', None)
    query_param = request.args.get('q', '', type=str)
    if current_user.access_level == 'administrador':
        base_query = Ticket.query
    elif current_user.access_level == 'tecnico':
        base_query = Ticket.query.filter(or_(Ticket.target_sector == current_user.sector, Ticket.origin_sector == current_user.sector, Ticket.assigned_to == current_user.id))
    else:
        base_query = Ticket.query.filter_by(user_id=current_user.id)
    if query_param:
        search_term = f"%{query_param}%"
        base_query = base_query.filter(or_(Ticket.title.ilike(search_term), cast(Ticket.id, String).ilike(search_term)))
    tickets = base_query.order_by(Ticket.priority.desc(), Ticket.created_at.asc()).all()
    return render_template('tickets_kanban.html', title='Kanban de Chamados', tickets=tickets)

@main.route('/update_ticket_status/<int:ticket_id>', methods=['POST'])
@login_required
def update_ticket_status(ticket_id):
    if not is_tecnico():
        return jsonify({'success': False, 'message': 'Permissão negada.'}), 403
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    new_status = data.get('new_status')
    if not new_status:
        return jsonify({'success': False, 'message': 'Novo status não fornecido.'}), 400
    old_status = ticket.status
    if old_status != new_status:
        try:
            if new_status == 'Fechado':
                ticket.closed_at = datetime.utcnow()
            else:
                ticket.closed_at = None
            ticket.status = new_status
            history_entry = TicketHistory(ticket_id=ticket.id, changed_by_user_id=current_user.id, field_changed='status', old_value=old_status, new_value=new_status)
            db.session.add(history_entry)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Status do chamado #{ticket.id} alterado para {new_status}.'})
        except Exception:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Erro ao salvar no banco de dados.'}), 500
    return jsonify({'success': False, 'message': 'O status já é o mesmo.'})

# --- ROTAS DE DASHBOARD E RELATÓRIOS ---
@main.route('/dashboard')
@login_required
def dashboard():
    if not is_tecnico(): abort(403)
    status_counts = db.session.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    status_data = [{'status': s, 'count': c} for s, c in status_counts]
    sector_counts = db.session.query(Ticket.target_sector, func.count(Ticket.id)).group_by(Ticket.target_sector).all()
    sector_data = [{'sector': s, 'count': c} for s, c in sector_counts]
    priority_counts = db.session.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
    priority_data = [{'priority': p, 'count': c} for p, c in priority_counts]
    total_tickets = Ticket.query.count()
    return render_template('dashboard.html', title='Dashboard', status_data=json.dumps(status_data), sector_data=json.dumps(sector_data), priority_data=json.dumps(priority_data), total_tickets=total_tickets)

@main.route('/reports')
@login_required
def reports():
    if not is_tecnico(): abort(403)
    def format_timedelta(td):
        if td is None: return "N/A"
        total_seconds = int(td.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        parts = []
        if days > 0: parts.append(f"{days}d")
        if hours > 0: parts.append(f"{hours}h")
        if minutes > 0: parts.append(f"{minutes}m")
        return " ".join(parts) if parts else "< 1m"
    tickets_per_user = db.session.query(User.name, func.count(Ticket.id).label('ticket_count')).join(Ticket, User.id == Ticket.user_id).group_by(User.name).order_by(func.count(Ticket.id).desc()).all()
    closed_tickets = Ticket.query.filter(Ticket.status == 'Fechado', Ticket.closed_at.isnot(None)).all()
    average_closing_time, closing_time_details = None, []
    if closed_tickets:
        total_seconds = sum([(t.closed_at - t.created_at).total_seconds() for t in closed_tickets])
        average_seconds = total_seconds / len(closed_tickets) if closed_tickets else 0
        average_closing_time_td = timedelta(seconds=average_seconds)
        average_closing_time = format_timedelta(average_closing_time_td)
        for ticket in closed_tickets:
            duration = ticket.closed_at - ticket.created_at
            closing_time_details.append({'id': ticket.id, 'title': ticket.title, 'author': ticket.author.name, 'duration_str': format_timedelta(duration)})
    return render_template('reports.html', title='Relatórios', tickets_per_user=tickets_per_user, average_closing_time=average_closing_time, closing_time_details=closing_time_details)

# --- ROTAS DE ADMINISTRAÇÃO ---
@main.route('/users', methods=['GET', 'POST'])
@login_required
def user_management():
    if not is_admin(): abort(403)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user_id_to_change = request.form.get('user_id')
        user_to_change = User.query.get_or_404(user_id_to_change)
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user_to_change.password = hashed_password
        db.session.commit()
        flash(f'A senha do usuário {user_to_change.name} foi alterada com sucesso!', 'success')
        return redirect(url_for('main.user_management'))
    users = User.query.order_by(User.name).all()
    return render_template('user_management.html', title='Gerenciar Usuários', users=users, form=form)

@main.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not is_admin(): abort(403)
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'danger')
        return redirect(url_for('main.user_management'))
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f'Usuário {user_to_delete.name} foi excluído com sucesso.', 'success')
    return redirect(url_for('main.user_management'))

@main.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if not is_admin(): abort(403)
    user_to_toggle = User.query.get_or_404(user_id)
    if user_to_toggle.id == current_user.id:
        flash('Você não pode bloquear sua própria conta.', 'danger')
        return redirect(url_for('main.user_management'))
    user_to_toggle.is_active = not user_to_toggle.is_active
    db.session.commit()
    status = "ativado" if user_to_toggle.is_active else "bloqueado"
    flash(f'O usuário {user_to_toggle.name} foi {status} com sucesso.', 'success')
    return redirect(url_for('main.user_management'))

@main.route('/backup', methods=['GET'])
@login_required
def backup():
    if not is_admin(): abort(403)
    backup_folder = current_app.config['BACKUP_FOLDER']
    os.makedirs(backup_folder, exist_ok=True)
    backups = sorted([f for f in os.listdir(backup_folder) if f.endswith('.db')], reverse=True)
    return render_template('backup.html', title='Backup do Sistema', backups=backups)

@main.route('/create_backup', methods=['POST'])
@login_required
def create_backup():
    if not is_admin(): abort(403)
    db_path = os.path.join(current_app.instance_path, 'site.db')
    backup_folder = current_app.config['BACKUP_FOLDER']
    os.makedirs(backup_folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f'site_{timestamp}.db'
    backup_path = os.path.join(backup_folder, backup_filename)
    try:
        shutil.copy2(db_path, backup_path)
        flash(f'Backup "{backup_filename}" criado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao criar o backup: {e}', 'danger')
    return redirect(url_for('main.backup'))

@main.route('/download_backup/<filename>')
@login_required
def download_backup(filename):
    if not is_admin(): abort(403)
    backup_folder = current_app.config['BACKUP_FOLDER']
    return send_from_directory(directory=backup_folder, path=filename, as_attachment=True)

@main.route('/delete_backup/<filename>', methods=['POST'])
@login_required
def delete_backup(filename):
    if not is_admin(): abort(403)
    backup_folder = current_app.config['BACKUP_FOLDER']
    file_path = os.path.join(backup_folder, filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'Backup "{filename}" excluído com sucesso.', 'success')
        else:
            flash('Arquivo de backup não encontrado.', 'warning')
    except Exception as e:
        flash(f'Erro ao excluir o backup: {e}', 'danger')
    return redirect(url_for('main.backup'))

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not is_admin():
        abort(403)
    form = SettingsForm()
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
        
    if form.validate_on_submit():
        settings.auto_close_days = form.auto_close_days.data
        
        # --- LÓGICA DE SALVAR LOGO ---
        if form.logo.data:
            logo_filename = save_logo(form.logo.data)
            if logo_filename:
                settings.logo_filename = logo_filename
                
        db.session.commit()
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('main.settings'))
        
    elif request.method == 'GET':
        form.auto_close_days.data = settings.auto_close_days
        
    return render_template('settings.html', title='Configurações', form=form)

@main.route('/check_updates')
@login_required
def check_updates():
    last_check_str = session.get('last_check_time')
    if not last_check_str:
        session['last_check_time'] = datetime.utcnow().isoformat()
        return jsonify(updates=[])
    last_check_dt = datetime.fromisoformat(last_check_str)
    updates_payload = []
    notified_tickets = set()
    new_tickets = Ticket.query.filter(Ticket.created_at > last_check_dt).all()
    for ticket in new_tickets:
        tecnicos_do_setor = User.query.filter_by(sector=ticket.target_sector, access_level='tecnico').all()
        admins = User.query.filter_by(access_level='administrador').all()
        notificar_para = set(tecnicos_do_setor + admins)
        if current_user in notificar_para and ticket.user_id != current_user.id:
            if ticket.id not in notified_tickets:
                message = f"Novo chamado #{ticket.id}: '{ticket.title}' aberto por {ticket.author.name}."
                updates_payload.append({'message': message, 'url': url_for('main.view_ticket', ticket_id=ticket.id)})
                notified_tickets.add(ticket.id)
    new_comments = Comment.query.filter(Comment.created_at > last_check_dt, Comment.user_id != current_user.id).all()
    for comment in new_comments:
        ticket = comment.ticket
        is_author = ticket.user_id == current_user.id
        is_assignee = ticket.assigned_to is not None and ticket.assigned_to == current_user.id
        if is_author or is_assignee:
            if ticket.id not in notified_tickets:
                message = f"Novo comentário no chamado #{ticket.id}: '{ticket.title}' por {comment.comment_author.name}."
                updates_payload.append({'message': message, 'url': url_for('main.view_ticket', ticket_id=ticket.id)})
                notified_tickets.add(ticket.id)
    session['last_check_time'] = datetime.utcnow().isoformat()
    return jsonify(updates=updates_payload)


# --- ROTAS DE CHAT (REESTRUTURADAS E CORRIGIDAS) ---

@main.route('/chat', methods=['GET'])
@login_required
def chat_users():
    sent_to_ids = db.session.query(ChatMessage.recipient_id).filter(ChatMessage.sender_id == current_user.id).distinct()
    received_from_ids = db.session.query(ChatMessage.sender_id).filter(ChatMessage.recipient_id == current_user.id).distinct()
    all_partner_ids = {row[0] for row in sent_to_ids}.union({row[0] for row in received_from_ids})

    conversations = []
    for partner_id in all_partner_ids:
        last_message = ChatMessage.query.filter(
            or_(
                (ChatMessage.sender_id == current_user.id) & (ChatMessage.recipient_id == partner_id),
                (ChatMessage.sender_id == partner_id) & (ChatMessage.recipient_id == current_user.id)
            )
        ).order_by(ChatMessage.timestamp.desc()).first()
        if last_message:
            conversations.append(last_message)
    
    conversations.sort(key=lambda x: x.timestamp, reverse=True)

    users_without_conversations = User.query.filter(
        User.id != current_user.id,
        ~User.id.in_(all_partner_ids)
    ).order_by(User.name).all()

    return render_template('chat_users.html', conversations=conversations, users_without_conversations=users_without_conversations, title="Chat")


@main.route('/chat/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def chat_conversation(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    form = ChatMessageForm()
    
    if form.validate_on_submit():
        attachment_filename = save_chat_attachment(form.attachment.data)
        msg = ChatMessage(sender_id=current_user.id,
                          recipient_id=recipient_id,
                          content=form.content.data,
                          attachment_filename=attachment_filename)
        db.session.add(msg)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        return redirect(url_for('main.chat_conversation', recipient_id=recipient_id))

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'errors': form.errors})

    return render_template('chat_conversation.html', form=form, recipient=recipient, title=f"Chat com {recipient.name}")


@main.route('/api/chat/<int:recipient_id>/messages')
@login_required
def get_chat_messages(recipient_id):
    query = ChatMessage.query.filter(
        or_(
            (ChatMessage.sender_id == current_user.id) & (ChatMessage.recipient_id == recipient_id),
            (ChatMessage.sender_id == recipient_id) & (ChatMessage.recipient_id == current_user.id)
        )
    )
    messages = query.order_by(ChatMessage.timestamp.asc()).all()
    messages_data = []
    for msg in messages:
        data = {
            'sender_name': msg.sender.name,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat() + 'Z',
            'is_current_user': msg.sender_id == current_user.id,
            'attachment_filename': msg.attachment_filename,
            'attachment_url': url_for('static', filename=f'chat_uploads/{msg.attachment_filename}') if msg.attachment_filename else None
        }
        messages_data.append(data)
    return jsonify(messages_data)

# --- NOVAS ROTAS PARA NOTIFICAÇÕES DE CHAT ---

@main.route('/api/chat/unread_info', methods=['GET'])
@login_required
def unread_info():
    """Retorna uma lista de IDs de remetentes que têm mensagens não lidas para o utilizador atual."""
    unread_senders = db.session.query(ChatMessage.sender_id).filter(
        ChatMessage.recipient_id == current_user.id,
        ChatMessage.is_read == False
    ).distinct().all()
    # Extrai os IDs da lista de tuplos
    sender_ids = [s[0] for s in unread_senders]
    return jsonify({'unread_senders': sender_ids})


@main.route('/api/chat/<int:sender_id>/mark_as_read', methods=['POST'])
@login_required
def mark_as_read(sender_id):
    """Marca todas as mensagens de um remetente específico como lidas."""
    messages_to_update = ChatMessage.query.filter(
        ChatMessage.sender_id == sender_id,
        ChatMessage.recipient_id == current_user.id,
        ChatMessage.is_read == False
    ).all()
    
    for msg in messages_to_update:
        msg.is_read = True
    
    db.session.commit()
    return jsonify({'success': True})
    
# --- ROTAS DE AJUDA E ERRO ---
@main.route('/help')
@login_required
def help():
    return render_template('help.html', title='Ajuda')

@main.errorhandler(403)
def forbidden(error):
    flash('Você não tem permissão para acessar esta página.', 'danger')
    return render_template('403.html', title='Acesso Negado'), 403

@main.errorhandler(404)
def not_found(error):
    flash('A página que você está procurando não existe.', 'danger')
    return render_template('404.html', title='Página Não Encontrada'), 404