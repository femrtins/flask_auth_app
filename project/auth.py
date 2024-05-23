from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    
    
    email = request.form['email']
    senha = request.form['senha']

    # Tem que fazer isso funcionar ainda
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # Checa se o usuário já existe
    # Pega a senha dada pelo usuário passa o hash e compara com a senha no bd
    if not user or not check_password_hash(user.password, senha):
        flash('Erro! Confira seus dados e tente novamente')
        # Se o usuário não existe ou a senha está errada, atualiza a pagina
        return redirect(url_for('auth.login'))

    # Se os anteriores passarem manda o usuário para o seu perfil
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template("signup.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

'''
Cadastrar usuário no banco de dados

! mudar a forma de saber se as senhas são iguais para o javascript, para que a página não atualize
! mudar para que primeiro o usuário coloque o e-mail, pressione continuar e seja direcionado para 
outra pagina onde ele precisará inserir as outras informações, para que a página não seja atualizada
e ele perca todos os dados se já existir um email igual no bd.
! mudar para que a senha seja salva com criptografia no banco de dados. OK
! mostrar cliente cadastrado antes de redirecionar para a página de login

'''
@auth.route('/signup', methods=['POST'])
def signup_post():
    nome = request.form['nome']
    username = request.form['user_name']
    email = request.form['email']
    senha = request.form['senha']
    senha_confirmacao = request.form['senha_comparacao']

    user = User.query.filter_by(email=email).first()
    user_n = User.query.filter_by(username=username).first()

    # Se o usuário não é encontrado, ele é redirecionado para a página de cadastro e recebe
    # a mensagem que o endereço de e-mail já exite
    if user: 
        flash('Esse e-mail já existe')
        return redirect(url_for('auth.signup'))
    if user_n:
        flash('Esse nome de usuário já existe')
        return redirect(url_for('auth.signup'))
    
    # Se as senhas não são iguais o usuário é redirecionado para a página de cadastro e recebe
    # a mensagem que as senhas não são iguais
    if senha != senha_confirmacao:
        flash('As senhas não são iguais')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=nome, username=username, password=generate_password_hash(senha, method='pbkdf2'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():

    bio = request.form['bio']
    name = request.form['name']
    username = request.form['username']
    photo = request.form['photo']

    # Verifica se o novo email não pertence a outro usuário
    if username != current_user.username and User.query.filter_by(username=username).first():
        flash('Esse nome de usuário já está em uso.')
        return redirect(url_for('profile'))

    # Atualiza as informações do usuário
    if bio != "":
        current_user.biograpy = bio
    if name != "":   
        current_user.name = name
    if username != "":      
        current_user.username = username
    if photo != "":    
        current_user.image_path = photo

	# Salva as alterações no banco de dados
    db.session.commit()
    flash('Informações do perfil atualizadas com sucesso!')
    return redirect(url_for('editar_perfil'))