from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,GroupRequest,Group
from app import db,bcrypt
from app.helpers import login_required,get_object_or_404

admin_blueprint = Blueprint('admin',__name__)


@admin_blueprint.route('/groups/<int:group_id>/admin/')
@login_required
def admin_panel(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if user in group.admins:
        return render_template('admin.html',group=group,)
    else:
        flash('You are not an admin')
        return redirect(url_for('groups.group_page',group_id=group_id))

@admin_blueprint.route('/groups/<int:group_id>/admin/requests/')
@login_required
def group_requests(group_id):
    group = get_object_or_404(Group,Group.id == group_id)
    if group.private:
        requests = GroupRequest.query.filter_by(group=group_id)
        users_from = []
        for r in requests:
            user = User.query.get(r.user)
            users_from.append((r,user))
        l = len(users_from)
        return render_template('requests.html',len=l,users_from=users_from,is_group=True,group=group)
    else:
        flash("Group is public no requests")
        return redirect(url_for('admin.admin_panel',group_id=group_id))

@admin_blueprint.route('/groups/<int:group_id>/admin/requests/<int:request_id>/accept/')
@login_required
def accept(group_id,request_id):
    group = get_object_or_404(Group,Group.id == group_id)
    user = User.query.get(session['user_id'])
    if user in group.admins:
        request = get_object_or_404(GroupRequest,GroupRequest.id == request_id)
        request.accept(request.user,group.id)
        flash('Request accepted')
        return redirect(url_for('admin.group_requests',group_id=group_id))

@admin_blueprint.route('/groups/<int:group_id>/admin/requests/<int:request_id>/reject/')
@login_required
def reject(group_id,request_id):
    group = get_object_or_404(Group,Group.id == group_id)
    user = User.query.get(session['user_id'])
    if user in group.admins:
        request = get_object_or_404(GroupRequest,GroupRequest.id == request_id)
        request.reject()
        flash('Request rejected')
        return redirect(url_for('admin.group_requests',group_id=group_id))

#make a user an admin
@admin_blueprint.route('/groups/<int:group_id>/members/<int:user_id>/make_admin/')
@login_required
def make_admin(group_id,user_id):
    admin = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if group.is_admin(admin): #check if current user is an admin
        user = get_object_or_404(User,User.id == user_id)
        group.make_admin(user)
        redirect(url_for('groups.members',group_id=group_id))
    else:
        flash('You do not have permission for that')
        redirect(url_for('groups.group_page',group_id=group_id))

#Delete a post
@admin_blueprint.route('/group/<int:group_id>/post/<int:post_id>/delete/')
@login_required
def delete_post(group_id,post_id):
    post = get_object_or_404(Post,Post.id==post_id)
    group = get_object_or_404(Group,Group.id==group_id)
    user = User.query.get(session['user_id'])
    if post.poster == session['user_id'] or user in group.admins:       
        group.group_posts.remove(post)
        db.session.commit()
        post.delete()
        flash('POST deleted')
        return redirect(url_for('groups.group_page',group_id=group_id))
    else:
        flash("You do not have permission for that")
        return redirect(url_for('posts.post',post_id = post_id))

@admin_blueprint.route('/groups/<int:group_id>/members/<int:user_id>/remove/')
@login_required
def remove_member(group_id,user_id):
    group = get_object_or_404(Group,Group.id == group_id)
    admin = User.query.get(session['user_id'])
    if group.is_admin(admin):
        user = get_object_or_404(User,User.id == user_id)
        if not group.is_admin(user):
            group.members.remove(user)
            db.session.commit()
            #group.leave(user)
            flash('Member removed')
        else:
            flash('Admins can remove admins')
        return redirect(url_for('groups.members',group_id=group_id))
    else:
        flash('You do not have permission to remove someone from a group')
        return redirect(url_for('groups.group_page',group_id=group_id))


@admin_blueprint.route('/groups/<int:group_id>/admin/change_privacy/')
@login_required
def change_privacy(group_id):
    group = get_object_or_404(Group,Group.id==group_id)
    user = User.query.get(session['user_id'])
    if user in group.admins:
        if group.private == True:
            group.private = False
            requests = GroupRequest.query.filter_by(group=group_id)
            for r in requests:
                r.accept(r.user,group.id)
            flash('Group made public')
        else:
            group.private = True
            flash('Group made private')
        db.session.commit()
        return redirect(url_for('admin.admin_panel',group_id=group_id))
    else:
        flash('You do not have permission for that')
        return redirect(url_for('groups.group_page',group_id=group_id))


