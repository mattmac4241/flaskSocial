from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import Post,User,Comment
from app import db
from app.helpers import login_required,get_object_or_404

comments_blueprint = Blueprint('comments',__name__)

@comments_blueprint.route('/posts/<int:post_id>/create_comment/',methods=['GET','POST'])
@login_required
def create_comment(post_id):
	if request.method == 'POST':
		user = User.query.get(session['user_id'])
		comment = Comment(
				content = request.form['content'],
				poster = user.id,
				parent = post_id,
				poster_name = user.user_name
				)
		db.session.add(comment)
		db.session.commit()
		flash('Comment made')
		return redirect(url_for('posts.post',post_id=post_id))

@comments_blueprint.route('/posts/<int:post_id>/comment/<int:comment_id>/delete/')
@login_required
def delete_comment(post_id,comment_id):
	post = Post.query.get(post_id)
	if session['user_id'] == post.poster:
		Comment.query.filter_by(comment_id).delete()
		db.session.commit()
		flash('Comment removed')
	else:
		flash('You do not have permission for that')
	return redirect(url_for('posts.post',post_id=post_id))

