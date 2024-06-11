from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Post

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")


@main.route('/profile/<username>')
# @login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@main.route('/stream')
def stream():
    posts = Post.query.all()
    return render_template('stream.html', posts=posts)

@main.route('/search')
def search_posts():
    query = request.args.get('query')
    posts = Post.query.filter(Post.post.ilike(f'%{query}%')).all()
    return render_template('stream.html', posts=posts)