from functools import wraps
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,Group,Post
from app import db
from .forms import GroupForm
from app.helpers import login_required,get_object_or_404


groups_blueprint = Blueprint('groups',__name__)

@groups_blueprint.route('/groups/')
@login_required
def groups():
    user = User.query.get(session['user_id'])
    groups = user.groups
    return render_template('groups.html',groups=groups)

@groups_blueprint.route('/groups/<int:group_id>/')
@login_required
def group_page(group_id):
    group = get_object_or_404(Group,Group.id == group_id)
    return render_template('group.html',group=group)

@groups_blueprint.route('/groups/create/',methods=['GET','POST'])
@login_required
def create_group():
    error = None
    form = GroupForm(request.form)
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        is_private = False
        if form.private.data == 'private':
            is_private = True
        new_group = Group(
            name = form.name.data,
            description = form.description.data,
            private = is_private,
            admin = user,
        )
        try:
            db.session.add(new_group)
            db.session.commit()
            return redirect(url_for('groups.group_page',group_id=new_group.id))
        except IntegrityError:
            flash('Group name already taken')
            return render_template('create_group.html',form=form)
    return render_template('create_group.html',form=form)


@groups_blueprint.route('/groups/<int:group_id>/create_group_post/',methods=['GET','POST'])
@login_required
def create_post(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if request.method == 'POST':
        post = Post(
            title = request.form['title'],
            content = request.form['content'],
            poster = user.id,
            poster_name = user.user_name
            )
        try:
            db.session.add(post)
            db.session.commit()
            group.add_post(post)
        except IntegrityError:
            flash("Something went wrong")
        return redirect(url_for('groups.group_page',group_id=group_id))
    return render_template('create_post.html',user=False,group=group)


@groups_blueprint.route('/groups/<int:group_id>/join/')
@login_required
def join_group(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if user not in group.members:
        group.join(user)
    else:
        flash('You already joined this group')
    return redirect(url_for('groups.group_page',group_id=group_id))

@groups_blueprint.route('/groups/<int:group_id>/leave/')
@login_required
def leave_group(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if user not in group.members:
        flash('You can\'t leave a group you are not apart of')
    else:
        group.leave(user)
    return redirect(url_for('groups.groups'))

@groups_blueprint.route('/groups/<int:group_id>/members/')
@login_required
def members(group_id):
    group = get_object_or_404(Group,Group.id == group_id)
    members = group.members
    return render_template('members.html',members=members)


@groups_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/remove/')
@login_required
def remove_member(group_id,member_id):
    group = get_object_or_404(Group,Group.id == group_id)
    admin = User.query.get(session['user_id'])
    if group.is_admin(admin):
        user = get_object_or_404(User,User.id == user_id)
        if not group.is_admin(user):
            group.leave(user)
            flash('Member removed')
        else:
            flash('Admins can remove admins')
        return redirect(url_for('groups.members',group_id=group_id))
    else:
        flash('You do not have permission to remove someone from a group')
        return redirect(url_for('groups.group_page',group_id=group_id))


#make a user an admin
@groups_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/make_admin/')
@login_required
def make_admin(group_id,user_id):
    admin = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if group.is_admin(user): #check if current user is an admin
        user = get_object_or_404(User,User.id == user_id)
        group.make_admin(user)
        redirect(url_for('groups.members',group_id=group_id))
    else:
        flash('You do not have permission for that')
        redirect(url_for('groups.group_page',group_id=group_id))

@groups_blueprint.route('/groups/<int:group_id>/admins/')
@login_required
def get_admins(group_id):
    group = get_object_or_404(Group,Group.id == group_id)
    admins = group.admins
    return render_template('admins.html',admins=admins)





