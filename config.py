import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
     # --- CONFIGURAÇÃO ADICIONADA ---
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Limite de 16MB para uploads