import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from datetime import datetime
import pytz # Importa a biblioteca para fusos horários

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa as extensões globalmente
db = SQLAlchemy()
login_manager = LoginManager()

# Configurações do Flask-Login
login_manager.login_view = 'main.login'
login_manager.login_message = "Por favor, faça o login para acessar esta página."
login_manager.login_message_category = "info"


# --- FILTRO JINJA2 CUSTOMIZADO PARA DATAS E HORAS LOCAIS ---
def format_datetime_local(value, format='%d/%m/%Y %H:%M'):
    """
    Filtro Jinja para converter uma data/hora UTC do banco de dados 
    para o fuso horário local de São Paulo.
    """
    if value is None:
        return ""
    
    # Define os fusos horários de origem (UTC) e destino (local)
    utc_tz = pytz.utc
    local_tz = pytz.timezone('America/Sao_Paulo') # Você pode mudar para seu fuso horário
    
    # Adiciona a informação de que a data do banco é UTC
    utc_dt = utc_tz.localize(value)
    
    # Converte para o fuso horário local
    local_dt = utc_dt.astimezone(local_tz)
    
    return local_dt.strftime(format)


def create_app():
    """Cria e configura a instância da aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # --- REGISTRA O FILTRO JINJA2 NA APLICAÇÃO ---
    app.jinja_env.filters['localdatetime'] = format_datetime_local

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Importa os modelos e rotas dentro do contexto da aplicação
        from app import models, forms
        from app.routes import main as main_blueprint
        
        app.register_blueprint(main_blueprint)
        
        # Cria as tabelas do banco de dados, se não existirem
        db.create_all()

        # Cria um usuário administrador padrão na primeira execução
        if not models.User.query.filter_by(email='admin@empresa.com').first():
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
            admin_user = models.User(
                name='Administrador',
                email='admin@empresa.com',
                sector='TI',
                password=hashed_password,
                access_level='administrador'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário administrador padrão criado!")

        # Cria as configurações padrão do sistema na primeira execução
        if not models.SystemSettings.query.first():
            settings = models.SystemSettings()
            db.session.add(settings)
            db.session.commit()
            print("Configurações padrão do sistema criadas!")

    return app

@login_manager.user_loader
def load_user(user_id):
    """Função callback do Flask-Login para carregar um usuário pelo ID."""
    from app.models import User
    return User.query.get(int(user_id))