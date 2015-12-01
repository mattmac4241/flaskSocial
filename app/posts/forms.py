from flask_wtf import Form
from wtforms import StringField,TextAreaField
from wtforms.validators import DataRequired,Length

class PostForm(Form):
    title = StringField(
        'title',
        validators=[DataRequired(),Length(min=1,max=300)]
    )
    content = TextAreaField(
        'Content',
        validators=[DataRequired(),Length(min=1,max=15000)]
    )

    