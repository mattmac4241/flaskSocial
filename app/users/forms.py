from flask_wtf import Form
from wtforms import StringField,PasswordField,SelectField
from wtforms.validators import DataRequired,Length,EqualTo,Email

class RegisterForm(Form):
    user_name = StringField(
        'user_name',
        validators=[DataRequired(),Length(min=1,max=50)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(),Email(),Length(min=6,max=40)]
    )
  
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)])

    confirm = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password')]
    )

class LoginForm(Form):
    email = StringField(
        'Email',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

class ChangePasswordForm(Form):
    password = PasswordField(
        'Old Password',
        validators=[DataRequired(), Length(min=6, max=40)]
    )
    new_password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)]
        )
    confirm = PasswordField(
        'Repeat New Password',
        validators=[DataRequired(), EqualTo('new_password')]
    )


class ResetPasswordForm(Form):
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=6, max=40)]
        )
    confirm = PasswordField(
        'Repeat New Password',
        validators=[DataRequired(), EqualTo('new_password')]
    )


    


    