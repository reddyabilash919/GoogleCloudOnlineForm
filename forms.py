from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed





class RegistrationForm(FlaskForm):

    id = StringField('ID',
                     validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired()])
    user_image = FileField('Upload Image', validators=[
        FileAllowed(['jpg', 'png']), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

#   user_Image =
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    id = StringField('ID',
                     validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')


class PostForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])
    picture = FileField('Upload Image', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


class UpdatePasswordForm(FlaskForm):
   old_password = PasswordField(
       'Old Password', validators=[DataRequired()])
   new_password = PasswordField(
       'New Password', validators=[DataRequired()])
   submit = SubmitField('Update')


class EditPostForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])
    picture = FileField('Upload Image', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
