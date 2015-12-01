from functools import wraps
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,Group 
from app import db,bcrypt
from .forms import GroupForm
import os
from unicodedata import normalize


groups_blueprint = Blueprint('groups',__name__)

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

def slugify(text, encoding=None,
         permitted_chars='abcdefghijklmnopqrstuvwxyz0123456789-'):
    if isinstance(text, str):
        text = text.decode(encoding or 'ascii')
    clean_text = text.strip().replace(' ', '-').lower()
    while '--' in clean_text:
        clean_text = clean_text.replace('--', '-')
    ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
    strict_text = map(lambda x: x if x in permitted_chars else '', ascii_text)
    return ''.join(strict_text)

@groups_blueprint.route('/groups/')
@login_required
def groups():
    user = User.query.get(session['user_id'])
    groups = user.groups
    return render_template('groups.html',groups=groups)

@groups_blueprint.route('/groups/<int:group_id>/')
@login_required
def group_page(group_id):
    group = Group.query.get(group_id)
    return render_template('group.html',group=group)

@groups_blueprint.route('/groups/create/',methods=['GET','POST'])
@login_required
def create_group():
    error = None
    form = GroupForm(request.form)
    if request.method == 'POST':
        slug = ''
        user = User.query.get(session['user_id'])
        is_private = False
        if form.private.data == 'private':
            is_private = True
        new_group = Group(
            name = form.name.data,
            description = form.description.data,
            private = is_private,
            admin = user,
            slug = slugify(form.name.data)
        )
        try:
            db.session.add(new_group)
            db.session.commit()
            return redirect(url_for('groups.group_page',id=new_group.id))
        except IntegrityError:
            flash('Group name already taken')
            return render_template('create_group.html',form=form)
    return render_template('create_group.html',form=form)

@groups_blueprint.route('/groups/<int:group_id>/join/')
@login_required
def join_group(group_id):
    user = User.query.get(session['user_id'])
    group = Group.query.get(group_id)
    if user not in group.members:
        group.join(user)
    else:
        flash('You already joined this group')
    return redirect(url_for('groups.group_page',group_id=group_id))

@groups_blueprint.route('/groups/<int:group_id>/leave/')
@login_required
def leave_group(group_id):
    user = User.query.get(session['user_id'])
    group = Group.query.get(group_id)
    if user not in group.members:
        flash('You can\'t leave a group you are not apart of')
    else:
        group.leave(user)
    return redirect(url_for('groups.groups'))










