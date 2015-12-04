from functools import wraps
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from app.models import User,Group,Post,GroupRequest
from app import db,app
from .forms import GroupForm
from app.helpers import login_required,get_object_or_404,get_sort_posts


groups_blueprint = Blueprint('groups',__name__)

#all of the user's groups
@groups_blueprint.route('/groups/')
@login_required
def groups():
    user = User.query.get(session['user_id'])
    groups = user.groups
    return render_template('groups.html',groups=groups,user=user,search=False)

'''
Sort comments by either most liked,which is default,
else sort by new,least,or oldest
'''
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

#create a group, either a public or private group
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

'''Join group if group is private
a request is sent to the group an admin of the group
then can accept or reject that request, and then the member is added
else user just joins the group
'''
@groups_blueprint.route('/groups/<int:group_id>/join/')
@login_required
def join_group(group_id):
    group = get_object_or_404(Group,Group.id == group_id) #check if group exists
    user = User.query.get(session['user_id'])
    if user not in group.banned_members:
        if user not in group.members:
            check = GroupRequest.query.filter_by(user = session['user_id'],group= group.id).first() #get friend request
            if group.private:
                if check == None: #if no request present
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
    else:
        flash('You are banned from this group')
    return redirect(url_for('groups.group_page',group_id=group_id))

#leave group, can't leave if you are an admin
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

#get the members of the page
@groups_blueprint.route('/groups/<int:group_id>/members/')
@login_required
def members(group_id):
    user = User.query.get(session['user_id'])
    group = get_object_or_404(Group,Group.id == group_id)
    admins = group.admins 
    is_admin = group.is_admin(user) #check if the user is an admin
    members = group.members
    return render_template('members.html',members=members,admins=admins,is_admin=is_admin,group=group)

#like/unlike a post depending on if user already liked the post
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
