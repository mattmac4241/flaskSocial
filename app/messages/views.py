from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,Message
from app import db,bcrypt
import os
from app.helpers import login_required,get_object_or_404

message_blueprint = Blueprint('messages',__name__)

@message_blueprint.route('/send_message/<int:user_id>/',methods=['GET','POST'])
@login_required
def send_message(user_id):
	if request.method == 'POST':
		if user_id != session['user_id']:
			message = Message(
				user_to = User.query.get(user_id).id,
				user_from = User.query.get(session['user_id']).id,
				content = request.form['message']
				)
			db.session.add(message)
			db.session.commit()
			flash('Message sent')
			return redirect(url_for('users.profile',user_id=user_id))
		else:
			flash('Can\'t send a message to yourself')
			return redirect(url_for('users.profile',user_id=user_id))

	
@message_blueprint.route('/user/messages/')
@login_required
def messages():
	m = Message.query.filter_by(user_to=session['user_id'])
	messages = []
	for mes in m:
		user= User.query.get(mes.user_from)
		messages.append((mes,user))
	are_messages = len(messages) > 0
	return render_template('messages.html',messages=messages,are_messages=are_messages)

@message_blueprint.route('/messages/<int:message_id>/')
@login_required
def read_message(message_id):
	message = get_object_or_404(Message,Message.id == message_id)
	if session['user_id'] == message.user_to:
		user_from = User.query.get(message.user_from)
		message.read = True
		return render_template('message.html',message=message,user_from=user_from)
	else:
		flash("You do not have permiession for that")
		return redirect(url_for('messages.messages'))

@message_blueprint.route('/messages/<int:message_id>/delete/')
@login_required
def delte_message(message_id):
	message = get_object_or_404(Message,Message.id == message_id)
	if session['user_id'] == message.user_to:
		db.session.delete(message)
		db.session.commit()
		flash('Message deleted')
		return redirect(url_for('messages.messages'))
	elif session['user_id'] != message.user_to:
		flash("You do not have permiession for that")
		return redirect(url_for('messages.messages'))


	