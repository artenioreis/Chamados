from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

# --- LINHA ADICIONADA AQUI ---
login_manager.login_message = "Por favor, faça o login para acessar esta página."
login_manager.login_message_category = "info" # Opcional: define a cor do alerta (Bootstrap)

login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app import models, forms
        
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        db.create_all()

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

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))