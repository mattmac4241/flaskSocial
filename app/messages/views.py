from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,Message
from app import db,bcrypt
import os
from app.helpers import login_required,get_object_or_404

message_blueprint = Blueprint('messages',__name__)

#send a message to a user
@message_blueprint.route('/send_message/<int:user_id>/',methods=['GET','POST'])
@login_required
def send_message(user_id):
	if request.method == 'POST':
		if user_id != session['user_id']: #can't send message to yourself
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

#get the user's messages	
@message_blueprint.route('/user/messages/')
@login_required
def messages():
	m = Message.query.filter_by(user_to=session['user_id'])
	messages = []
	for mes in m: #loop through messages and get them
		user= User.query.get(mes.user_from) #add user to a tupple containg the user and the message
		messages.append((mes,user))
	are_messages = len(messages) > 0 
	return render_template('messages.html',messages=messages,are_messages=are_messages)

#read message displays the message
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

#delete the message if user is the one it is sent to
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


	