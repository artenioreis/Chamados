from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash # Importe generate_password_hash aqui
import os
from dotenv import load_dotenv

load_dotenv() # Carrega variáveis de ambiente do arquivo .env

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login' # Define a rota de login, usando o nome do blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config') # Carrega configurações

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app import models, forms # Importa modelos e formulários
        
        # Importa e registra o Blueprint de rotas
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        db.create_all() # Cria as tabelas no banco de dados

        # Cria um usuário administrador padrão se não existir
        if not models.User.query.filter_by(email='admin@empresa.com').first():
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256') # Corrigido para 'pbkdf2:sha256'
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

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))