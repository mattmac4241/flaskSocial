from functools import wraps
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from .forms import PostForm
from app.models import Post,User,Comment
from app import db,bcrypt
from app.helpers import login_required,get_object_or_404

posts_blueprint = Blueprint('posts',__name__)


@posts_blueprint.route('/create_post/',methods=['GET','POST'])
@login_required
def create_post():
	user = User.query.get(session['user_id'])
	if request.method == 'POST':
		post = Post(
			title = request.form['title'],
			content = request.form['content'],
			poster = user.id
			)
		
		try:
			db.session.add(post)
			db.session.commit()
		except IntegrityError:
			flash("Something went wrong")
			return render_template('create_post.html',error=error)
	return render_template('create_post.html',user=True)


@posts_blueprint.route('/post/<int:post_id>/')
@login_required
def post(post_id):
	post = get_object_or_404(Post,Post.id==post_id)
	comments = Comment.query.filter_by(parent=post.id)
	return render_template('post.html',post=post,comments=comments)

@posts_blueprint.route('/post/<int:post_id>/delete/')
@login_required
def delete_post(post_id):
	post = get_object_or_404(Post,Post.id==post_id)
	print post.title
	if post.poster == session['user_id']:
		comments = Comment.query.filter_by(parent=post_id).all()
		for comment in comments:
			comment.delete()
		db.session.delete(post)
		db.session.commit()
		flash('POST deleted')
		return redirect(url_for('users.profile',user_id = session['user_id']))
	else:
		flash("You do not have permission for that")
		return redirect(url_for('posts.post',post_id = post_id))

@posts_blueprint.route('/post/<int:post_id>/like/')
@login_required
def like_post(post_id):
	post = get_object_or_404(Post,Post.id == post_id)
	user = User.query.get(session['user_id'])
	if user not in post.likes:
		post.like(user)
	elif user in post.likes:
		post.unlike(user)
	return redirect(url_for('posts.post',post_id=post_id))

