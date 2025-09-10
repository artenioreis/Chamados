import os
import shutil
from datetime import datetime
from app import create_app

def run_backup():
    """
    Cria uma instância da aplicação Flask para acessar as configurações
    e executa a lógica de backup do banco de dados.
    """
    app = create_app()
    with app.app_context():
        db_path = os.path.join(app.instance_path, 'site.db')
        backup_folder = app.config['BACKUP_FOLDER']
        
        # Garante que a pasta de backup exista
        os.makedirs(backup_folder, exist_ok=True)
        
        # Define o nome do arquivo de backup com data e hora
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'site_{timestamp}.db'
        backup_path = os.path.join(backup_folder, backup_filename)
        
        try:
            # Copia o arquivo do banco de dados para a pasta de backup
            shutil.copy2(db_path, backup_path)
            print(f'Backup criado com sucesso: {backup_filename}')
        except Exception as e:
            print(f'ERRO ao criar backup: {e}')

if __name__ == '__main__':
    print("Iniciando o script de backup agendado...")
    run_backup()
    print("Script de backup finalizado.")