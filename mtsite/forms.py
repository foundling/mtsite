from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, Length, Required, DataRequired, Email, EqualTo
from mtsite.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], default='aramsdell')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()], default='Alex')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    token = StringField('Token', validators=[Required(), Length(6,6)])
    remember_me = BooleanField('Remember Me')

    submit = SubmitField('Login')


