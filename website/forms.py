from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class SignUp(FlaskForm):
    user_name = StringField("name", validators=[DataRequired(), Length(max=100)])
    email = EmailField("email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("password", validators=[DataRequired(), Length(min=7)])
    password_again = PasswordField("password_again", validators=[DataRequired(), Length(min=7)])
    submit = SubmitField("signup")

class Login(FlaskForm):
    email = EmailField("email", validators=[DataRequired(),Length(max=100)])
    password = PasswordField("password",validators=[DataRequired(),Length(min=7)])
    submit = SubmitField("login")

class UpdateUser(FlaskForm):
    email = EmailField("email", validators=[Length(max=100)])
    user_name = StringField("user_name", validators=[Length(max=100)])
    submit = SubmitField("update")

class PostForm(FlaskForm):
    text = TextAreaField("text", validators=[DataRequired()])
    submit = SubmitField("post")