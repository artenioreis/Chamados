from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models import User

# NOVO FORMULÁRIO ADICIONADO
class StartConversationForm(FlaskForm):
    subject = StringField('Assunto da Conversa', validators=[DataRequired(), Length(min=3, max=150)])
    submit = SubmitField('Iniciar Conversa')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    sector = SelectField('Setor', choices=[
        ('TI', 'TI'), ('Vendas', 'Vendas'), ('Faturamento', 'Faturamento'),
        ('Contas a Pagar', 'Contas a Pagar'), ('Contas a Receber', 'Contas a Receber'),
        ('RH', 'RH'), ('Marketing', 'Marketing'), ('Outros', 'Outros')
    ], validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    access_level = SelectField('Nível de Acesso', choices=[
        ('colaborador', 'Colaborador'), ('tecnico', 'Técnico'), ('administrador', 'Administrador')
    ], validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este e-mail já está em uso. Por favor, escolha outro.')

class TicketForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10)])
    attachment = FileField('Anexar Imagem (Print)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Apenas imagens são permitidas!')
    ])
    
    origin_sector = SelectField('Setor de Origem', choices=[
        ('TI', 'TI'), ('Vendas', 'Vendas'), ('Faturamento', 'Faturamento'),
        ('Contas a Pagar', 'Contas a Pagar'), ('Contas a Receber', 'Contas a Receber'),
        ('RH', 'RH'), ('Marketing', 'Marketing'), ('Outros', 'Outros')
    ], validators=[DataRequired()])
    
    target_sector = SelectField('Setor de Destino', choices=[
        ('TI', 'TI'), ('Vendas', 'Vendas'), ('Faturamento', 'Faturamento'),
        ('Contas a Pagar', 'Contas a Pagar'), ('Contas a Receber', 'Contas a Receber'),
        ('RH', 'RH'), ('Marketing', 'Marketing'), ('Outros', 'Outros')
    ], validators=[DataRequired()])
    
    priority = SelectField('Prioridade', choices=[
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Abrir Chamado')

class CommentForm(FlaskForm):
    content = TextAreaField('Adicionar um novo comentário', validators=[DataRequired(), Length(min=5)])
    attachment = FileField('Anexar Arquivo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'],
                    'Apenas imagens, PDFs, documentos e texto são permitidos!')
    ])
    submit_comment = SubmitField('Adicionar Comentário')

class TicketUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Aberto', 'Aberto'), ('Em Atendimento', 'Em Atendimento'),
        ('Resolvido', 'Resolvido'), ('Fechado', 'Fechado')
    ], validators=[DataRequired()])
    priority = SelectField('Prioridade', choices=[
        ('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta')
    ], validators=[DataRequired()])
    assigned_to = SelectField('Atribuído a', choices=[], coerce=int)
    submit_update = SubmitField('Atualizar Chamado')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Alterar Senha')

class ChatMessageForm(FlaskForm):
    content = TextAreaField('Mensagem', validators=[Length(min=0, max=500)])
    attachment = FileField('Anexo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'],
                    'Apenas imagens, PDFs, documentos e texto são permitidos!')
    ])
    submit = SubmitField('Enviar')

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        if not self.content.data and not self.attachment.data:
            self.content.errors.append('Você precisa enviar uma mensagem ou um anexo.')
            return False
        return True

class SettingsForm(FlaskForm):
    auto_close_days = IntegerField('Fechar chamados "Resolvidos" após (dias)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Salvar Configurações')