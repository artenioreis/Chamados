# Sistema de Chamados Internos (Kanban)

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

Um sistema web simples e funcional para gerenciamento de chamados internos de uma empresa, utilizando uma interface no estilo Kanban. Desenvolvido com Flask e SQLAlchemy, é ideal para pequenas e médias equipes que precisam organizar solicitações entre diferentes setores.

## 📋 Funcionalidades Principais

-   **Autenticação de Usuários:** Sistema de login seguro com senhas criptografadas.
-   **Níveis de Acesso:** Perfis de `Colaborador`, `Técnico` e `Administrador` com diferentes permissões.
-   **Abertura de Chamados:** Formulário completo para criar novos chamados com título, descrição, setor de origem/destino e prioridade.
-   **Anexos:** Permite anexar imagens (prints de tela, etc.) na abertura de um chamado.
-   **Visualização Kanban:** Organize e visualize todos os chamados em colunas (Aberto, Em Atendimento, Resolvido, Fechado).
-   **Drag-and-Drop:** Mova chamados entre as colunas do Kanban para atualizar o status de forma rápida e visual.
-   **Detalhes e Comentários:** Página de detalhes para cada chamado com histórico de alterações e um sistema de comentários para interação.
-   **Busca:** Funcionalidade de busca por título ou número (ID) do chamado.
-   **Gerenciamento de Usuários (Admin):** Administradores podem cadastrar, excluir, bloquear/desbloquear e alterar a senha de outros usuários.
-   **Dashboard:** Gráficos simples para visualização de métricas (chamados por status, setor, prioridade).
-   **Relatórios:** Métricas sobre os usuários que mais abrem chamados e o tempo médio de fechamento.

## 🛠️ Tecnologias Utilizadas

-   **Backend:** Python 3, Flask
-   **Banco de Dados:** SQLite (para simplicidade e portabilidade)
-   **ORM:** SQLAlchemy
-   **Frontend:** HTML5, CSS3, JavaScript
-   **Framework CSS:** Bootstrap 5
-   **Templates:** Jinja2
-   **Bibliotecas Python:** Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug, python-dotenv, pytz.

## 🚀 Instalação e Execução

Siga os passos abaixo para rodar o projeto localmente.

### 1. Pré-requisitos

-   Python 3.8 ou superior
-   `pip` (gerenciador de pacotes do Python)

### 2. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio



Feito com ❤️ por Artenio Reis.














