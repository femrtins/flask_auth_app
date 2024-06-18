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

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/stream')
def stream():

    page = request.args.get('page', 1, type=int)  # Pega o número da página da consulta de URL, padrão para 1

    filter_type = request.args.get('filter', 'all')  # Pega o parâmetro de consulta 'filter'

    if filter_type == 'following':
        following_ids = current_user.get_following_ids()
        posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.timestamp.desc()).paginate(page=page, per_page=10)
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=POSTS_PER_PAGE )

    return render_template('stream.html', posts=posts, filter_type=filter_type)


@main.route('/search_posts', methods=['GET'])
def search_posts():
    query = request.args.get('query')
    if query:
        # Pesquisar posts que contêm a consulta no conteúdo, nome ou username
        results = Post.query.join(User).filter(
            (Post.post.ilike(f'%{query}%')) |
            (User.username.ilike)(f'%{query}%')|
            (User.name.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return render_template('stream.html', query=query, posts=results)




@main.route('/seguindo/<username>')
def get_seguindo(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('seguindo.html', user=user)

@main.route('/seguidores/<username>')
def get_seguidores(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('seguidores.html', user=user)



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



@main.route('/books',  methods=['GET'])
def search_books():
    
    query = request.args.get('query')
    if not query:
        return render_template('books.html')
    api_results = search_in_google_books(query)

    return render_template('books.html', query=query, api_results=api_results)


@main.route('/book/<book_id>', methods=['GET', 'POST'])
def book_details(book_id):

    book = get_book_details(book_id)
    comments = Rating.query.filter_by(book_id=book_id).order_by(Rating.timestamp.desc()).all()


    if book:
        
        return render_template('book.html', book=book, comments=comments)
    else:
        flash('Detalhes do livro não disponíveis.')
        return redirect(url_for('main.index'))

@main.route('/add_rating', methods=['POST'])
@login_required
def add_rating():
    comment_text = request.form.get('text')
    book_id = request.form.get('book_id')  
    rate = request.form.get('fb')
    if not comment_text:
        flash('Comment cannot be empty')
        return redirect(url_for('main.book_details', book_id=book_id)) 

    comment = Rating(user_id=current_user.id, book_id=book_id, text=comment_text, rate=rate)
    db.session.add(comment)
    db.session.commit()
    flash('Comment added successfully!')

    return redirect(url_for('main.book_details', book_id=book_id)) 

@main.route('/del_rating/<int:rating_id>', methods=['POST'])
@login_required
def delete_rating(rating_id):
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        flash('Você não tem permissão para excluir este post.')
        return redirect(url_for('auth.profile', username=current_user.username))  
    try:
        db.session.delete(rating)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir o post: {str(e)}')    
    return redirect(url_for('auth.profile', username=current_user.username))

def get_book_details(book_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(url)
    if response.status_code == 200:
        book = response.json()
        if 'volumeInfo' in book:
            return book
    return None


@main.route('/edit_rating/<int:rating_id>', methods=['GET','POST'])
@login_required
def edit_rating(rating_id):

    rating = Rating.query.get_or_404(rating_id)

    if rating.user_id != current_user.id:
        flash('Você não tem permissão para editar este post.')
        return redirect(url_for('auth.profile', username=current_user.username))  
    
    if request.method== 'POST':

        edited_text = request.form.get('edited-rating')

        rating.text = edited_text

        rating.timestamp = datetime.now()
                
        try:

            db.session.commit()
            flash('Post atualizado com sucesso!')

        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar o post: {str(e)}') 
            
        return redirect(url_for('auth.profile', username=current_user.username))
    
