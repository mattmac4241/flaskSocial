from app.helpers import login_required,get_object_or_404
from app.models import Group
from app import db,bcrypt
from flask import flash, redirect, render_template,request, session, url_for, Blueprint
from sqlalchemy_searchable import search

search_blueprint = Blueprint('search',__name__)

#return the results for searching for a group
@search_blueprint.route('/groups/search/',methods=['GET','POST'])
@login_required
def search_groups():
    if request.method == 'POST':
        term = request.form['search'] #get the term from the search and perform search query 
        query = db.session.query(Group)
        groups = Group.query.search(term).all()
        return render_template('groups.html',groups=groups,search=True)
    return render_template('groups.html',groups=[],search=True)

