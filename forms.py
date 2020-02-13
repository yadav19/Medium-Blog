from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import Length, DataRequired, EqualTo, Email

class Register(FlaskForm):
    username = StringField("Username",validators=[DataRequired(), Length(max=20,min=4)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",validators=[DataRequired(), EqualTo("password")])
    submit_button = SubmitField("Sign Up")

class Login(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit_button = SubmitField("Log In")
