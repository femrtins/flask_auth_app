from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from markupsafe import Markup
from . import db
from .models import User, Post
from .models import User, Post, Rating
import requests
POSTS_PER_PAGE = 20

main = Blueprint('main', __name__)

'''
Função para entrar no perfil da pessoa
'''
@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.id.desc()).all()
    ratings = Rating.query.filter_by(user_id=user.id).order_by(Rating.id.desc()).all()


    for rating in ratings:
        book_details = get_book_details(rating.book_id)
        volume_info = book_details.get('volumeInfo', {})
        rating.book_title = volume_info.get('title', 'Título não disponível')
        rating.book_thumb = volume_info.get('imageLinks', {}).get('thumbnail')

    return render_template('profile.html', user=user, posts=posts, ratings=ratings)

'''
Rota para a página inicial
'''
@main.route('/')
def index():
    return render_template("index.html")

"""
Rota para a página de explorar
Contém todas as postagens e avaliações
"""
@main.route('/stream')
def stream():

    page = request.args.get('page', 1, type=int)  # Pega o número da página da consulta de URL, padrão para 1

    filter_type = request.args.get('filter', 'all')  # Pega o parâmetro de consulta 'filter'
    ratings=[]
    posts = []

    if filter_type == 'following':
        following_ids = current_user.get_following_ids()

        posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.timestamp.desc()).paginate(page=page, per_page=10)
        ratings = Rating.query.filter(Rating.user_id.in_(following_ids)).order_by(Rating.timestamp.desc()).paginate(page=page, per_page=POSTS_PER_PAGE )

    elif filter_type =='outro':
        ratings = Rating.query.order_by(Rating.timestamp.desc()).paginate(page=page, per_page=POSTS_PER_PAGE )

    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=POSTS_PER_PAGE )

    for rating in ratings:
            book_details = get_book_details(rating.book_id)
            volume_info = book_details.get('volumeInfo', {})
            rating.book_title = volume_info.get('title', 'Título não disponível')
            rating.book_thumb = volume_info.get('imageLinks', {}).get('thumbnail')
    
    return render_template('stream.html', posts=posts, filter_type=filter_type, ratings=ratings)


"""
Função que retorna os resultados da pesquisa da página de explorar
"""
@main.route('/search_posts', methods=['GET'])
def search_posts():
    query = request.args.get('query')
    if query:
        # Pesquisar posts que contêm a consulta no conteúdo, nome ou username
        results1 = Post.query.join(User).filter(
            (Post.post.ilike(f'%{query}%')) |
            (User.username.ilike)(f'%{query}%')|
            (User.name.ilike(f'%{query}%'))
        ).all()

        results2 = Rating.query.join(User).filter(
            (Rating.text.ilike(f'%{query}%')) |
            (User.username.ilike)(f'%{query}%')|
            (User.name.ilike(f'%{query}%'))
        ).all()

        for rating in results2:
            book_details = get_book_details(rating.book_id)
            volume_info = book_details.get('volumeInfo', {})
            rating.book_title = volume_info.get('title', 'Título não disponível')
            rating.book_thumb = volume_info.get('imageLinks', {}).get('thumbnail')
        
    else:
        results1 = []
        results2
    return render_template('stream.html', query=query, posts=results1, ratings = results2)


"""
Rota para a página que contém os seguidores do usuário está seguindo
"""

@main.route('/seguindo/<username>')
def get_seguindo(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('seguindo.html', user=user)

"""
Rota para a página que contém os seguidores do usuário
"""
@main.route('/seguidores/<username>')
def get_seguidores(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('seguidores.html', user=user)


"""
Função que pesquisa os livros da API google books.
Retorna um dicionário dentro de uma lista, contendo informações sobre o livro:
- informação do livro
- título da obra
- imagem da obra
- id do livro

"""

def search_in_google_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        books = response.json().get('items', [])
        results = []
        for item in books:
            book_info = item.get('volumeInfo', {})
            title = book_info.get('title')
            thumbnail = book_info.get('imageLinks', {}).get('thumbnail', '')
            book_id = item.get('id')
            results.append({'title': title, 'thumbnail': thumbnail, 'book_id': book_id})
        return results
    return []

"""
Rota para a página dos livros.
"""
@main.route('/books',  methods=['GET'])
def search_books():
    
    query = request.args.get('query')
    if not query:
        return render_template('books.html')
    api_results = search_in_google_books(query)

    return render_template('books.html', query=query, api_results=api_results)

"""
Rota para a página individual de cada livro
"""
@main.route('/book/<book_id>', methods=['GET', 'POST'])
def book_details(book_id):

    book = get_book_details(book_id)
    comments = Rating.query.filter_by(book_id=book_id).order_by(Rating.timestamp.desc()).all()


    if book:
        
        return render_template('book.html', book=book, comments=comments)
    else:
        flash('Detalhes do livro não disponíveis.')
        return redirect(url_for('main.index'))


""""
Função que adiciona uma postagem com avaliação da obra (rating) no banco de dados.
"""
@main.route('/add_rating', methods=['POST'])
@login_required
def add_rating():
    comment_text = request.form.get('text')
    book_id = request.form.get('book_id')  
    rate = request.form.get('rate')
    if not comment_text:
        flash('Comentário não pode ser vazio.')
        return redirect(url_for('main.book_details', book_id=book_id)) 
    
    if not rate:
        rate = 0

    comment = Rating(user_id=current_user.id, book_id=book_id, text=comment_text, rate=rate)
    db.session.add(comment)
    db.session.commit()
    flash('Comentário adicionado!')

    return redirect(url_for('main.book_details', book_id=book_id)) 


"""
Função que deleta uma postagem com avaliação da obra (rating) no banco de dados
"""
@main.route('/del_rating/<int:rating_id>', methods=['POST'])
@login_required
def delete_rating(rating_id):
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        flash('Você não tem permissão para excluir este post.')
        return redirect(url_for('main.profile', username=current_user.username))  
    try:
        db.session.delete(rating)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir o post: {str(e)}')    
    return redirect(url_for('main.profile', username=current_user.username))

"""
Função que retorna informações sobre um livro específico da api.
"""
def get_book_details(book_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(url)
    if response.status_code == 200:
        book = response.json()
        if 'volumeInfo' in book:
            return book
    return None

"""
Função que edita uma postagem com avaliação da obra (rating) no banco de dados.
"""
@main.route('/edit_rating/<int:rating_id>', methods=['GET','POST'])
@login_required
def edit_rating(rating_id):

    rating = Rating.query.get_or_404(rating_id)

    if rating.user_id != current_user.id:
        flash('Você não tem permissão para editar este post.')
        return redirect(url_for('main.profile', username=current_user.username))  
    
    if request.method== 'POST':

        edited_text = request.form.get('edited-rating')
        rating.text = edited_text
        rating.timestamp = datetime.now()

        rate_value = request.form.get(f'rate-{rating_id}')
        
        if rate_value is not None:
            rating.rate = int(rate_value)
        else:
            rating.rate = 0
        try:

            db.session.commit()
            flash('Post atualizado com sucesso!')

        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar o post: {str(e)}') 
            
        return redirect(url_for('main.profile', username=current_user.username))