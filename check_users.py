from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("--- USUÁRIOS NO BANCO ---")
    for u in users:
        print(f"ID: {u.id} | Nome: {u.name} | Email: {u.email} | Nível: {u.access_level} | Ativo: {u.is_active}")
    print("--------------------------")
