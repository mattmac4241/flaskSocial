from functools import wraps
from sqlalchemy.orm import exc
from werkzeug.exceptions import abort
from flask import session,flash,redirect,url_for

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

def get_object_or_404(model, *criterion):
    try:
        return model.query.filter(*criterion).one()
    except exc.NoResultFound, exc.MultipleResultsFound:
        abort(404)

#get posts sorted depending on url
def get_sort_posts(group,url):
    posts = []
    if 'new' in url:
        posts = [(x,x.time_posted) for x in group.group_posts]
        posts.sort(key=lambda x: x[1])
        posts.reverse()
    
    elif 'old' in url:
        posts = [(x,x.time_posted) for x in group.group_posts]
        posts.sort(key=lambda x: x[1])

    elif 'least' in url:
        posts = [(x,len(x.likes)) for x in group.group_posts]
        posts.sort(key=lambda x: x[1])

    else:
        posts = [(x,len(x.likes)) for x in group.group_posts]
        posts.sort(key=lambda x: x[1])
        posts.reverse()

    return posts

