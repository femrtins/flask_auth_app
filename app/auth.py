from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file,jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Post, Follow
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from datetime import datetime
from io import BytesIO
from .models import User, Post, Rating

auth = Blueprint('auth', __name__)


@auth.route('/del_user/<int:user_id>', methods=['POST'])
def del_user(user_id):

    user = User.query.get_or_404(user_id)
    db.session.delete(user)

    db.session.commit()
    return redirect(url_for('auth.login'))

'''
Rota do form de login
'''
@auth.route('/login')
def login():
    return render_template('login.html')


'''
Rota da busca

'''
@auth.route('/search')
def search():
    return render_template('stream.html')


'''
Rota do form de login
'''
@auth.route('/login', methods=['POST'])
def login_post():
    
    
    email = request.form['email']
    senha = request.form['senha']

    # Tem que fazer isso funcionar ainda
    remember = request.form.get('remember')

    user = User.query.filter_by(email=email).first()

    # Checa se o usuário já existe
    # Pega a senha dada pelo usuário passa o hash e compara com a senha no bd
    if not user or not check_password_hash(user.password, senha):
        flash('Erro! Confira seus dados e tente novamente')
        # Se o usuário não existe ou a senha está errada, atualiza a pagina
        return redirect(url_for('auth.login'))

    # Se os anteriores passarem manda o usuário para o seu perfil
    login_user(user, remember=remember)

    return redirect(url_for('main.profile', username=user.username))



'''
Rota do cadastro

'''
@auth.route('/signup')
def signup():
    return render_template("signup.html")


'''
Rota do para deslogar

'''
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
        flash('E-mail já existente.')
        return redirect(url_for('auth.signup'))
    if user_n:
        flash('Nome de usuário já existente.')
        return redirect(url_for('auth.signup'))
    
    if len(senha)<6:
        flash('A senha deve ter pelo menos 6 caracteres.')
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

    flash('Usuário cadastrado.')
    return redirect(url_for('auth.login'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



'''
Função que retorna o arquivo se ele for permitido
'''
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route('/editar')
def editar():
    return render_template('editar.html', user = current_user)

'''
Editar perfil
'''

@auth.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    if request.method == 'POST':

        bio = request.form.get('bio')
        name = request.form.get('nome')
        username = request.form.get('username')
        photo = request.files.get('photo')

        print(photo)
        # Verifica se o novo email não pertence a outro usuário
        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Esse nome de usuário já está em uso.')
            return redirect(url_for('main.profile'))

        # Atualiza as informações do usuário
        if bio:
            current_user.biography = bio
        if name:   
            current_user.name = name           
        if username:      
            current_user.username = username
        if photo and allowed_file(photo.filename):
            photo_bytes = photo.read()
            current_user.image = photo_bytes
        
        # Salva as alterações no banco de dados
        try:
            db.session.commit()
            flash('Informações do perfil atualizadas com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar o perfil: {str(e)}')
    return redirect(url_for('main.profile', username=current_user.username))



'''
Postar um post 
'''
@auth.route('/post', methods=['GET','POST'])
@login_required
def post():
    if request.method == 'POST':
        post_content = request.form.get('post')

        if post_content:
            new_post = Post(post=post_content, user_id=current_user.id, username=current_user.username) # Associar post ao usuário atual
            db.session.add(new_post)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Ocorreu um erro ao criar o post: {str(e)}')
                
    return redirect(url_for('main.profile', username=current_user.username))



'''
Editar um post 
'''
@auth.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Verifica se o usuário atual é o autor do post
    if post.author != current_user:
        flash('Você não tem permissão para editar este post.')
        return redirect(url_for('main.profile', username=current_user.username))

    if request.method == 'POST':
        edited_post = request.form.get('edited-post')

        # Atualiza o conteúdo do post no banco de dados
        post.post = edited_post
        post.timestamp = datetime.now()

        try:
            db.session.commit()
            flash('Post atualizado com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar o post: {str(e)}')

        return redirect(url_for('main.profile', username=current_user.username))

    # Renderiza o template de edição de post
    return render_template('edit_post.html', post=post)



'''
Deletar um post 
'''
@auth.route('/del_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('Você não tem permissão para excluir este post.')
        return redirect(url_for('main.profile', username=current_user.username))  
    try:
        db.session.delete(post)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir o post: {str(e)}')
    
    return redirect(url_for('main.profile', username=current_user.username))




'''
Função para pegar a foto do usuario do bd
'''
@auth.route('/user/image/<int:user_id>')
def get_user_image(user_id):
    user = User.query.get_or_404(user_id)
    if not user.image:
        # Se o usuário não tiver uma imagem, retorne uma imagem padrão ou uma mensagem de erro
        return send_file('static/img/foto.png')
    return send_file(BytesIO(user.image), mimetype='image/jpeg')


'''
Função para seguir outro usuário
'''
@auth.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    followed_user = User.query.get_or_404(user_id)    
    if Follow.query.filter_by(follower_id=current_user.id, followed_id=followed_user.id).first():
        return '', 204
    follow = Follow(follower_id=current_user.id, followed_id=followed_user.id)
    db.session.add(follow)
    db.session.commit()
    return redirect(url_for('main.profile', username=followed_user.username))


'''
Função para deixar de seguir outro usuário
'''
@auth.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    followed_user = User.query.get_or_404(user_id)
    follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=followed_user.id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        return redirect(url_for('main.profile', username=followed_user.username))
    return '', 204