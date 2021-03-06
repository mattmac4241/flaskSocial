from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from .forms import RegisterForm,LoginForm,ChangePasswordForm,ResetPasswordForm
from app.models import User,FriendRequest,Post
from app import db,bcrypt
from app.helpers import login_required,get_object_or_404
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email


users_blueprint = Blueprint('users',__name__)

#check if users are friends
def are_friends(user1,user2):
    user1 = User.query.get(user1)
    user2 = User.query.get(user2)
    if user1.is_friend(user2):
        return True
    else:
        return False
'''the home page, if user is not logged in
take them to login page
else take them to their user page
'''
@users_blueprint.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('users.my_profile'))
    else:
        return redirect(url_for('users.login')) 

#user register
@users_blueprint.route('/register/',methods=['GET','POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                user_name = form.user_name.data,
                email = form.email.data,
                password = bcrypt.generate_password_hash(form.password.data),
                confirmed = False
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                token = generate_confirmation_token(new_user.email)
                confirm_url = url_for('users.confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(new_user.email, subject, html)
                flash('A confirmation email has been sent via email.')
                return redirect(url_for('users.login'))

            except IntegrityError:
                error = "That username and/or email alread exists."
                return render_template('register.html',form=form,error=error)
    return render_template('register.html',form=form)

#user login
@users_blueprint.route('/login/',methods=['GET','POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=request.form['email']).first()
            if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
                if user.confirmed == True:
                        session['logged_in'] = True
                        session['user_id'] = user.id
                        flash('Welcome!')
                        flash("Succesfful Logged in")
                        return redirect(url_for('users.my_profile'))
                else:
                    flash('Please confirm your account, an email was sent')
            else:
                flash('Invlaid username or password')
                
    return render_template('login.html',form=form,error=error)

@users_blueprint.route('/logout/',methods=['GET','POST'])
def logout():
    session.pop('logged_in',None)
    session.pop('user_id',None)
    flash('Goodbye!')
    return redirect(url_for('users.login'))

@users_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        flash('Request new link')
        return redirect(url_for('users.resend_confirmation'))
    if email == False:
        flash('The confirmation link is invalid or has expired.', 'danger')
        flash('Request new link')
        return redirect(url_for('users.resend_confirmation'))
    print email
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('users.login'))

#resend confimation email if user
@users_blueprint.route('/resend/confimation/',methods=['GET','POST'])
def resend_confirmation():
    if request.method == 'POST':
        user = get_object_or_404(User,User.email == request.form['email'])
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('users.confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)
        flash('A new confirmation email has been sent.', 'success')
        return redirect(url_for('users.login'))
    return render_template('resend.html')

#changes password 
@users_blueprint.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    email = ''
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        flash('Request new link')
        return redirect(url_for("users.resend_password"))
    if email == False:
        flash('The confirmation link is invalid or has expired.', 'danger')
        flash('Request new link')
        return redirect(url_for('users.resend_password'))
    form = ResetPasswordForm(request.form)
    if request.method == 'POST':
        user = get_object_or_404(User,User.email == email)
        if form.validate_on_submit():
            user.password = bcrypt.generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed', 'success')
            return redirect(url_for('users.login'))
    return render_template('reset_password.html',form=form,token=token)

#resend confimation email if user
@users_blueprint.route('/resend/password/',methods=['GET','POST'])
def resend_password():
    if request.method == 'POST':
        user = get_object_or_404(User,User.email==request.form['email'])
        token = generate_confirmation_token(user.email)
        reset_url = url_for('users.reset_password', token=token, _external=True)
        html = render_template('reset.html', reset_url=reset_url)
        subject = "Reset Password"
        send_email(user.email, subject, html)
        flash('A reset password email has been sent.', 'success')
        return redirect(url_for('users.login'))
    return render_template('resend.html')

@users_blueprint.route('/change_password/',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.get(session['user_id'])
            if bcrypt.check_password_hash(user.password, request.form['password']):
                user.password = bcrypt.generate_password_hash(form.new_password.data)
                db.session.commit()
                flash('Password reset')
                return redirect(url_for('users.my_profile'))
            flash('Password does not match')
    return render_template('change_password.html',form=form,reset=True)


#the posts are filtered by newest post
#this is the user page 
@users_blueprint.route('/user/<int:user_id>/')
@login_required
def profile(user_id):
    user = get_object_or_404(User,User.id == user_id)
    user_profile = user.id == session['user_id']
    u = User.query.get(session['user_id'])
    posts = Post.query.filter_by(poster=user.id,self_post=True)
    posts = [(x,x.time_posted) for x in posts]
    posts.sort(key=lambda x: x[1])
    posts.reverse()
    friends = u in user.friends #check if the user is friends with the user
    if request.method == 'POST':
        print request.form 
        message = Message(
            user_to = User.query.get(user_id),
            user_from = User.query.get(session['user_id']),
            content = request.form['message']
            )
        db.session.add(message)
        db.session.commit()
    return render_template('user.html',user=user,user_profile=user_profile,friends=friends,posts=posts)

#add a new friend
@users_blueprint.route('/user/<int:user_id>/add_friend/',methods=['GET','POST'])
@login_required
def add_friend(user_id):
    check = FriendRequest.query.filter_by(user_sent_from = session['user_id'],user_sent_to = user_id).first() #get friend request
    friends = are_friends(session['user_id'],user_id)
    if check == None and not friends:
        fq = FriendRequest(
            user_sent_from = session['user_id'],
            user_sent_to = user_id
        )
        db.session.add(fq)
        db.session.commit()
        flash('Friend request sent!')
        return redirect(url_for('users.profile',user_id = user_id))
    else:
        if friends == True:
            flash('Already friends')
        else:
            flash('Request already sent')
        return redirect(url_for('users.profile',user_id = user_id))

#the user's requests
@users_blueprint.route('/user/requests/')
@login_required
def requests():
    user_to = User.query.get(session['user_id'])
    reqs = FriendRequest.query.filter_by(user_sent_to=user_to.id).all()
    users_from = []
    for r in reqs:
        user = User.query.get(r.user_sent_from)
        users_from.append((r,user))
    l = len(users_from)
    return render_template('requests.html',users_from=users_from,len=l)

#accept a friend request
@users_blueprint.route('/user/requests/<int:request_id>/accept/')
@login_required
def accept(request_id):
    request = get_object_or_404(FriendRequest,FriendRequest.id == request_id)
    if session['user_id'] == request.user_sent_to:
        request.accept()
        flash('Request accepted')
        return redirect(url_for('users.requests'))
    else:
        flash('Not allowed')
        return redirect(url_for('users.requests'))

#reject a friend request
@users_blueprint.route('/user/requests/<int:request_id>/reject/')
@login_required
def reject(request_id):
    request = get_object_or_404(FriendRequest,FriendRequest.id == request_id)
    if session['user_id'] == request.user_sent_to:
        request.reject()
        flash('Request rejected')
        return redirect(url_for('users.requests'))
    else:
        flash('Not allowed')
        return redirect(url_for('users.requests'))

#the user's friends
@users_blueprint.route('/user/friends/')
@login_required
def friends():
    user = User.query.get(session['user_id'])
    return render_template('friends.html',user=user)

#delete a user friend
@users_blueprint.route('/user/friends/<int:user_id>/delete/')
@login_required
def delete_friend(user_id):
    friend = get_object_or_404(User,User.id == user_id)
    user = User.query.get(session['user_id'])
    if user.is_friend(friend):
        user.delete_friend(friend)
        flash('User removed from friends list')
        return redirect(url_for('users.friends'))
    else:
        return redirect(url_for('users.friends'))
        
#the users own profile
@users_blueprint.route('/user/')
@login_required
def my_profile():
    user = User.query.get(session['user_id'])
    posts = Post.query.filter_by(poster=user.id,self_post=True)
    posts = [(x,x.time_posted) for x in posts]
    posts.sort(key=lambda x: x[1])
    posts.reverse()
    return render_template('user.html',user=user,user_profile = True,posts=posts)



