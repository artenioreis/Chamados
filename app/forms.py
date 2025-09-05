from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    sector = SelectField('Setor', choices=[
        ('TI', 'TI'),
        ('Vendas', 'Vendas'),
        ('Faturamento', 'Faturamento'),
        ('Contas a Pagar', 'Contas a Pagar'),
        ('Contas a Receber', 'Contas a Receber'),
        ('RH', 'RH'),
        ('Marketing', 'Marketing'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    access_level = SelectField('Nível de Acesso', choices=[
        ('colaborador', 'Colaborador'),
        ('tecnico', 'Técnico'),
        ('administrador', 'Administrador')
    ], validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este e-mail já está em uso. Por favor, escolha outro.')

class TicketForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10)])
    origin_sector = SelectField('Setor de Origem', choices=[
        ('TI', 'TI'),
        ('Vendas', 'Vendas'),
        ('Faturamento', 'Faturamento'),
        ('Contas a Pagar', 'Contas a Pagar'),
        ('Contas a Receber', 'Contas a Receber'),
        ('RH', 'RH'),
        ('Marketing', 'Marketing'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    target_sector = SelectField('Setor de Destino', choices=[
        ('TI', 'TI'),
        ('Vendas', 'Vendas'),
        ('Faturamento', 'Faturamento'),
        ('Contas a Pagar', 'Contas a Pagar'),
        ('Contas a Receber', 'Contas a Receber'),
        ('RH', 'RH'),
        ('Marketing', 'Marketing'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    priority = SelectField('Prioridade', choices=[
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta')
    ], validators=[DataRequired()])
    submit = SubmitField('Abrir Chamado')

class CommentForm(FlaskForm):
    content = TextAreaField('Adicionar um novo comentário', validators=[DataRequired(), Length(min=5)])
    # ALTERADO: Nome do campo de submit é único
    submit_comment = SubmitField('Adicionar Comentário')

class TicketUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Aberto', 'Aberto'),
        ('Em Atendimento', 'Em Atendimento'),
        ('Resolvido', 'Resolvido'),
        ('Fechado', 'Fechado')
    ], validators=[DataRequired()])
    priority = SelectField('Prioridade', choices=[
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta')
    ], validators=[DataRequired()])
    assigned_to = SelectField('Atribuído a', choices=[], coerce=int)
    # ALTERADO: Nome do campo de submit é único
    submit_update = SubmitField('Atualizar Chamado')