from flask import render_template, url_for, flash, redirect, request, abort, jsonify, Blueprint
from app import db # Importa 'db' da instância global de app
from app.forms import LoginForm, RegistrationForm, TicketForm, CommentForm, TicketUpdateForm
from app.models import User, Ticket, Comment, TicketHistory
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash # Importe generate_password_hash e check_password_hash aqui
from sqlalchemy import func, or_
import json

# Cria uma instância de Blueprint
main = Blueprint('main', __name__)

# Funções auxiliares para verificar nível de acesso
def is_admin():
    return current_user.is_authenticated and current_user.access_level == 'administrador'

def is_tecnico():
    return current_user.is_authenticated and (current_user.access_level == 'tecnico' or current_user.access_level == 'administrador')

@main.route('/')
@main.route('/home')
@login_required
def home():
    if current_user.access_level == 'administrador':
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    elif current_user.access_level == 'tecnico':
        # Técnicos veem chamados do seu setor e os que estão atribuídos a eles
        tickets = Ticket.query.filter(
            or_(
                Ticket.target_sector == current_user.sector,
                Ticket.assigned_to == current_user.id
            )
        ).order_by(Ticket.created_at.desc()).all()
    else: # Colaborador
        tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('index.html', title='Início', tickets=tickets)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home')) # Referência a rota usando blueprint.route_name
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Bem-vindo, {user.name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
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
        abort(403) # Somente administradores podem registrar usuários

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256') # Corrigido para 'pbkdf2:sha256'
        user = User(
            name=form.name.data,
            email=form.email.data,
            sector=form.sector.data,
            password=hashed_password,
            access_level=form.access_level.data
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Conta criada para {form.name.data}! O usuário pode fazer login agora.', 'success')
        return redirect(url_for('main.register')) # Redireciona para o cadastro para cadastrar mais
    return render_template('register.html', title='Cadastrar Usuário', form=form)

@main.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id,
            origin_sector=form.origin_sector.data,
            target_sector=form.target_sector.data,
            priority=form.priority.data
        )
        db.session.add(ticket)
        db.session.commit()
        
        # Adiciona histórico de criação do chamado
        history_entry = TicketHistory(
            ticket_id=ticket.id,
            changed_by_user_id=current_user.id,
            field_changed='status',
            old_value='N/A',
            new_value='Aberto'
        )
        db.session.add(history_entry)
        db.session.commit()
        
        flash('Seu chamado foi aberto com sucesso!', 'success')
        return redirect(url_for('main.tickets_kanban'))
    # Preenche o setor de origem com o setor do usuário logado
    form.origin_sector.data = current_user.sector
    return render_template('create_ticket.html', title='Abrir Chamado', form=form)

@main.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Verifica permissão para ver o chamado
    if ticket.user_id != current_user.id and \
       not (is_tecnico() and (ticket.target_sector == current_user.sector or ticket.origin_sector == current_user.sector or is_admin())):
        abort(403) # Usuário não tem permissão para ver este chamado

    comment_form = CommentForm()
    update_form = TicketUpdateForm()

    # Preencher o campo assigned_to no formulário de atualização
    tecnicos = User.query.filter(or_(User.access_level == 'tecnico', User.access_level == 'administrador')).filter_by(sector=ticket.target_sector).all()
    # Adicionar uma opção "Não Atribuído" (id=0) para a seleção
    update_form.assigned_to.choices = [(0, 'Não Atribuído')] + [(t.id, t.name) for t in tecnicos]

    if request.method == 'GET':
        update_form.status.data = ticket.status
        update_form.priority.data = ticket.priority
        update_form.assigned_to.data = ticket.assigned_to if ticket.assigned_to else 0 # Define como 0 se não atribuído
    
    # Processar atualização do chamado
    if update_form.validate_on_submit() and 'update_ticket_submit' in request.form:
        # Apenas técnicos e administradores podem atualizar
        if not is_tecnico():
            abort(403)

        # Registrar histórico de mudanças
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
            history_entry = TicketHistory(
                ticket_id=ticket.id,
                changed_by_user_id=current_user.id,
                field_changed=field,
                old_value=old_val,
                new_value=new_val
            )
            db.session.add(history_entry)
        
        db.session.commit()
        flash('Chamado atualizado com sucesso!', 'success')
        return redirect(url_for('main.view_ticket', ticket_id=ticket.id))

    # Processar novo comentário
    if comment_form.validate_on_submit() and 'add_comment_submit' in request.form:
        comment = Comment(
            content=comment_form.content.data,
            user_id=current_user.id,
            ticket_id=ticket.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comentário adicionado!', 'success')
        return redirect(url_for('main.view_ticket', ticket_id=ticket.id))

    return render_template('view_ticket.html', 
                           title=ticket.title, 
                           ticket=ticket, 
                           comment_form=comment_form, 
                           update_form=update_form,
                           is_tecnico=is_tecnico(),
                           is_admin=is_admin())

@main.route('/tickets_kanban')
@login_required
def tickets_kanban():
    if current_user.access_level == 'administrador':
        tickets = Ticket.query.order_by(Ticket.priority.desc(), Ticket.created_at.asc()).all()
    elif current_user.access_level == 'tecnico':
        # Técnicos veem chamados do seu setor e os que estão atribuídos a eles
        tickets = Ticket.query.filter(
            or_(
                Ticket.target_sector == current_user.sector,
                Ticket.assigned_to == current_user.id
            )
        ).order_by(Ticket.priority.desc(), Ticket.created_at.asc()).all()
    else: # Colaborador
        tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.priority.desc(), Ticket.created_at.asc()).all()
    
    return render_template('tickets_kanban.html', title='Kanban de Chamados', tickets=tickets)


@main.route('/dashboard')
@login_required
def dashboard():
    if not is_tecnico():
        abort(403) # Apenas técnicos e administradores podem ver o dashboard

    # Chamados por status
    status_counts = db.session.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    status_data = [{'status': s, 'count': c} for s, c in status_counts]

    # Chamados por setor de destino
    sector_counts = db.session.query(Ticket.target_sector, func.count(Ticket.id)).group_by(Ticket.target_sector).all()
    sector_data = [{'sector': s, 'count': c} for s, c in sector_counts]

    # Chamados por prioridade
    priority_counts = db.session.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
    priority_data = [{'priority': p, 'count': c} for p, c in priority_counts]
    
    # Total de chamados
    total_tickets = Ticket.query.count()

    return render_template('dashboard.html', 
                           title='Dashboard',
                           status_data=json.dumps(status_data),
                           sector_data=json.dumps(sector_data),
                           priority_data=json.dumps(priority_data),
                           total_tickets=total_tickets)

@main.errorhandler(403)
def forbidden(error):
    flash('Você não tem permissão para acessar esta página.', 'danger')
    return render_template('403.html', title='Acesso Negado'), 403

@main.errorhandler(404)
def not_found(error):
    flash('A página que você está procurando não existe.', 'danger')
    return render_template('404.html', title='Página Não Encontrada'), 404