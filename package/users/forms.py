from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from package.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    submit = SubmitField('Register')

    @staticmethod
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already registered')

    @staticmethod
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email is already registered')


class LogInForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture',
                        validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    @staticmethod
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already registered')

    @staticmethod
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('This email is already registered')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset')

    @staticmethod
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is None:
            raise ValidationError('No account with that email')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                           validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(),  EqualTo('password')])
    submit = SubmitField('Reset Password')


class SearchForm(FlaskForm):
    query = StringField('Query',
                            validators=[DataRequired()])
    search = SubmitField('Search')


class UploadForm(FlaskForm):
    tags = StringField('Tags',
                            validators=[DataRequired()])
    picture = FileField('Select file',
                            validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Upload')


class SubscribeForm(FlaskForm):
    follow = SubmitField('Follow')
    unfollow = SubmitField('Unfollow')
