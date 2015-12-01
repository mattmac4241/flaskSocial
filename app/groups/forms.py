from flask_wtf import Form
from wtforms import StringField,SelectField
from wtforms.validators import DataRequired,Length


class GroupForm(Form):
    name = StringField(
        'group name',
        validators=[DataRequired(),Length(min=1,max=300)]
    )
    description = StringField(
        'description',
        validators=[DataRequired(),Length(min=1,max=1000)]
    )
    private = SelectField(
    	choices=[('pr','Private'),('pu','Public')]
    )