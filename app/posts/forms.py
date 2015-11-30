from flask_wtf import Form
from wtforms import StringField,PasswordField,SelectField
from wtforms.validators import DataRequired,Length,EqualTo,Email

class PostForm(Form):
    title = StringField(
        'title',
        validators=[DataRequired(),Length(min=1,max=300)]
    )
    content = StringField(
        'Content',
        validators=[DataRequired(),Email(),Length(min=1,max=15000)]
    )