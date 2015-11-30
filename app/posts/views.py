from functools import wraps
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from .forms import PostForm
from app.models import Post,User
from app import db,bcrypt
import os

posts_blueprint = Blueprint('posts',__name__)

#helper function
def login_required(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return test(*args,**kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap


@posts_blueprint.route('/create_post/',methods=['GET','POST'])
@login_required
def create_post():
	user = User.query.get(session['user_id'])
	#form = PostForm(request.form)
	if request.method == 'POST':
		print request.form
		post = Post(
			title = request.form['title'],
			content = request.form['content'],
			poster = user.id
			)
		print post.title
		print post.content
		try:
			db.session.add(post)
			db.session.commit()
		except IntegrityError:
			flash("Something went wrong")
			return render_template('create_post.html',error=error)
	return render_template('create_post.html')

@posts_blueprint.route('/post/<int:post_id>/')
@login_required
def post(post_id):
	post = Post.query.get(post_id)
	return render_template('post.html',post=post)

@posts_blueprint.route('/post/<int:post_id>/delete/')
@login_required
def delete_post(post_id):
	if post_id == session['user_id']:
		Post.query.filter_by(id=post_id).delete()
		flash('POST deleted')
		return redirect(url_for('users.profile',user_id = session['user_id']))
	else:
		flash("You do not have permission for that")
		return redirect(url_for('posts.post',post_id = post_id))

