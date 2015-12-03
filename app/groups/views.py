from functools import wraps
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,Group,Post,GroupRequest
from app import db,app
from .forms import GroupForm
from app.helpers import login_required,get_object_or_404,get_sort_posts


groups_blueprint = Blueprint('groups',__name__)

@groups_blueprint.route('/groups/')
@login_required
def groups():
    user = User.query.get(session['user_id'])
    groups = user.groups
    return render_template('groups.html',groups=groups,user=user,search=False)

#sort comments by most liked by default
@groups_blueprint.route('/groups/<int:group_id>/')
@groups_blueprint.route('/groups/<int:group_id>/new/')
@groups_blueprint.route('/groups/<int:group_id>/least/')
@groups_blueprint.route('/groups/<int:group_id>/oldest/')
@login_required
def group_page(group_id):
    group = get_object_or_404(Group,Group.id == group_id)
    print group.private
    user = User.query.get(session['user_id'])
    url = request.url_rule
    admin = user in group.admins
    posts = get_sort_posts(group,str(url))
    member = user in group.members #check if user is member and grant certain privaliges if so
    return render_template('group.html',group=group,user=user,member=member,posts=posts,admin=admin)

@groups_blueprint.route('/groups/create/',methods=['GET','POST'])
@login_required
def create_group():
    error = None
    form = GroupForm(request.form)
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        is_private = False
        if form.private.data == 'pr':
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


#for group post displayed on group not user profile
@groups_blueprint.route('/groups/<int:group_id>/create_group_post/',methods=['GET','POST'])
@login_required
def create_post(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if user in group.members:
        if request.method == 'POST':
            post = Post(
                title = request.form['title'],
                content = request.form['content'],
                poster = user.id,
                poster_name = user.user_name,
                self_post = False
                )
            if post.title.strip() == '' or post.content.strip() == '':
                flash("You cannot post an empty post")
            else:
                try:
                    db.session.add(post)
                    db.session.commit()
                    group.add_post(post)
                except IntegrityError:
                    flash("Something went wrong")
            return redirect(url_for('groups.group_page',group_id=group_id))
    else:
        flash('NOT A MEMBER,JOIN THE GROUP!')
        return redirect(url_for('groups.group_page',group_id=group_id))
    return render_template('create_post.html',user=False,group=group)

@groups_blueprint.route('/groups/<int:group_id>/join/')
@login_required
def join_group(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    if user not in group.members:
        check = GroupRequest.query.filter_by(user = session['user_id'],group= group.id).first() #get friend request
        if group.private:
            if check == None:
                request = GroupRequest(
                    user = user.id,
                    group = group.id,
                    )
                db.session.add(request)
                db.session.commit()
                flash('Group is private, request to join sent')
                return redirect(url_for('users.my_profile'))
            else:
                flash('Request already sent')
        else:
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
    elif group.is_admin(user):
        flash('You can\'t leave a group you are an admin of')
    else:
        group.leave(session['user_id'])
    return redirect(url_for('groups.groups'))

@groups_blueprint.route('/groups/<int:group_id>/members/')
@login_required
def members(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    admins = group.admins
    is_admin = group.is_admin(user)
    members = group.members
    return render_template('members.html',members=members,admins=admins,is_admin=is_admin,group=group)


@groups_blueprint.route('/groups/<int:group_id>/members/<int:user_id>/remove/')
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


#make a user an admin
@groups_blueprint.route('/groups/<int:group_id>/members/<int:user_id>/make_admin/')
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

@groups_blueprint.route('/groups/<int:group_id>/post/<int:post_id>/like/')
@login_required
def like_post(post_id,group_id):
    post = get_object_or_404(Post,Post.id == post_id)
    user = User.query.get(session['user_id'])
    if user not in post.likes:
        post.like(user)
    elif user in post.likes:
        post.unlike(user)
    return redirect(url_for('groups.group_page',group_id=group_id))

#Delete a post
@groups_blueprint.route('/group/<int:group_id>/post/<int:post_id>/delete/')
@login_required
def delete_post(group_id,post_id):
    post = get_object_or_404(Post,Post.id==post_id)
    if post.poster == session['user_id']:       
        group = get_object_or_404(Group,Group.id==group_id)
        group.group_posts.remove(post)
        db.session.commit()
        post.delete()
        flash('POST deleted')
        return redirect(url_for('groups.group_page',group_id=group_id))
    else:
        flash("You do not have permission for that")
        return redirect(url_for('posts.post',post_id = post_id))









































