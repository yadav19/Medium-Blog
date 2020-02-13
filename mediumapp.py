from flask import Flask, abort, render_template, redirect, flash, url_for, request
# from forms import Register, Login
import secrets, os
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from  flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

############################################
#FORMS

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, PasswordField 
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError

##############################################

app = Flask("__name__")
app.config["SECRET_KEY"] = "9e881d1a94b2125d8df30ab584403075"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

bcrypt =Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # works same as url_for and redirects to the login page if not logged in
login_manager.login_message_category = 'info'

###############################################
# login loader
 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#################################################
class PostForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired()])
    content = TextAreaField("Content",validators=[DataRequired()])
    submit = SubmitField("Post")

class Register(FlaskForm):
    username = StringField("Username",validators=[DataRequired(), Length(max=20,min=4)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",validators=[DataRequired(), EqualTo("password")])
    submit_button = SubmitField("Sign Up")

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists")
    
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists")


class Login(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit_button = SubmitField("Log In")

class AccountUpdate(FlaskForm):
    username = StringField("Username",validators=[DataRequired(), Length(max=20,min=4)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture",validators=[FileAllowed(["jpg","png"])] )
    # password = PasswordField("Password",validators=[DataRequired()])
    # confirm_password = PasswordField("Confirm Password",validators=[DataRequired(), EqualTo("password")])
    update_button = SubmitField("Update")

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user and current_user.username != username.data:
            raise ValidationError("Username already exists")
    
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user and current_user.email != email.data:
            raise ValidationError("Email already exists")
    # username = StringField("Username", validators=[length(max=20,min=6)],)
    # email = StringField("Email",validators=[Email()])
    # update_button = SubmitField("Update")

    # def validate_username(self,uername):
    #     user = Users.query.filter_by(username=username.data).first()
    #     if user:
    #         raise ValidationError("Username acquired!!!")

    # def validate_email(self,email):
    #     user = Users.query.filter_by(email=email.data).first()
    #     if user:
    #         raise ValidationError("Another user already exists with same email")


###############################################

# posts = [
#     {
#         'author': 'Corey Schafer',
#         'title': 'Blog Post 1',
#         'content': 'First post content',
#         'date_posted': 'April 20, 2018'
#     },
#     {
#         'author': 'Jane Doe',
#         'title': 'Blog Post 2',
#         'content': 'Second post content',
#         'date_posted': 'April 21, 2018'
#     }
# ]

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(30), nullable=False, default="default.jpg")
    posts = db.relationship("Posts", backref="author",lazy=True) # 1. which model does it relate to //2. what will be reference name of it the other model //3. True means load the data necessary in one go

    def __repr__(self):
        return "User({}, {}, {}, {})".format(self.id,self.username,self.email,self.profile_pic)

class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    post_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    title = db.Column(db.String(40), nullable=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) # u in users is small as sqlite saves the tables in small letters
    def __repr__(self):
        return "Post({}, {}, {})".format(self.pid, self.post_date, self.title)

@app.route("/")
@app.route("/index")
def index():
    posts = Posts.query.all()
    return render_template("index.html",posts=posts)

@app.route("/info")
def info():
    return render_template("info.html",title="ABOUT")



@app.route("/login",methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = Login()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next") # what it does is it return a url to the page that was originall if accessed eg- on account page if you are not logged in you will end up at login page so it'll rediect you to that page
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash("login Unsuccessful!!!","danger")
        return redirect(url_for('login'))
    return render_template("login.html",title="LOG IN",form=form)

def save_dp(form_pic):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_pic.filename)
    pic_name = random_hex + f_ext
    pic_path = os.path.join(app.root_path,"static",pic_name)
    output_size=(125,125)
    i = Image.open(form_pic)
    i.thumbnail(output_size)
    i.save(pic_path)
    return pic_name

@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    form = AccountUpdate()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.profile_pic = save_dp(form.picture.data)
        current_user.email = form.email.data
        db.session.commit()
        flash("Account updated","success")
        return redirect(url_for("profile"))
    elif request.method =="GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    dp = url_for('static',filename="{}".format(current_user.profile_pic))
    return render_template("profile.html",title=current_user.username,dp=dp,form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

 
@app.route("/register",methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = Register()
    if form.validate_on_submit():
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user =Users(username='{}'.format(form.username.data), email='{}'.format(form.email.data), password='{}'.format(hashed_password))
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e :
            db.create_all()
            db.session.commit()
        else:
            flash(" you have successfully registered {}".format(form.username.data),"success")
        return redirect(url_for('login'))
    return render_template("register.html",title="REGISTRATION",form = form)

@app.route("/post/new",methods=["GET","POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit() 
        flash("POST CREATED","success")
        return redirect(url_for("index"))
    return render_template("create_post.html", title="New Post",form=form, legend="Create Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Posts.query.get_or_404(post_id)
    return render_template("post.html",title=post.title,post=post)

@app.route("/post/<int:post_id>/update",methods=["GET", "POST"])
@login_required
def update_post(post_id):
    
    post = Posts.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        return render_template("create_post.html",title="Update Post",form=form, legend="Update Post")
    else:
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
        return redirect(url_for('post',post_id=post.id))
        
        # flash("you dont have the permission!!!")
        # return redirect(url_for("post",post_id=post.id))

@app.route("/post/<int:post_id>/delete")
def delete_post(post_id):
    post = Posts.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("index"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)