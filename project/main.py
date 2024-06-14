from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Post

POSTS_PER_PAGE = 20

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")


@main.route('/profile/<username>')
# @login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()     
    return render_template('profile.html', user=user, posts=posts)

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

@main.route('/search')
def search_posts():
    query = request.args.get('query')
    posts = Post.query.filter(Post.post.ilike(f'%{query}%')).all()
    return render_template('stream.html', posts=posts)