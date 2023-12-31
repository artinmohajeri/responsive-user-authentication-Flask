from flask import Flask, redirect, url_for, render_template, Blueprint, flash, request, session
from werkzeug.security import generate_password_hash
from .forms import *
from .models import *
from flask_login import login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3" #define the db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup/",methods=["GET","POST"])
def signup():
    form = SignUp()
    user_name, email, password, password_again = None, None, None, None
    if request.method == "POST":
        if form.validate_on_submit():
            user_name = form.user_name.data
            email = form.email.data
            password = form.password.data
            password_again = form.password_again.data
            email_exist = User.query.filter_by(email=form.email.data).first()
            user_name_exist = User.query.filter_by(user_name=form.user_name.data).first()
            if email_exist or user_name_exist:
                flash(message="The user already exists.", category="warning")
                return redirect(url_for("signup"))
            else:
                if password == password_again:
                    user = User(user_name=user_name, email=email, password = password)
                    db.session.add(user)
                    db.session.commit()
                    flash(message="signed up successfuly!", category="success")
                    return redirect(url_for("login"))
                else:
                    flash(message="Your password doesnt match.", category="warning")
                    return redirect(url_for("signup"))
        else:
            flash(message="Invalid Input.", category="warning")
            return redirect(url_for("signup"))
            
    else:
        return render_template("signup.html",
            form = form,
            user_name = user_name,
            email = email,
            password = password,
            password_again = password_again,
        )


login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login/", methods=["GET","POST"])
def login():
    form = Login()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if check_password_hash(user.password_hash, form.password.data):
                    login_user(user)
                    flash(message="loged in successfuly!", category="success")
                    return redirect(url_for("profile"))
                else:
                    flash("wrong password. try again", category="warning")
                    return redirect(url_for("login"))
            else:
                flash("That user dosnt exist. try again.", category="warning")
                return redirect(url_for("login"))
        else:
            return render_template("login.html", form=form)
    else:
        return render_template("login.html",
            form = form,
        )


@app.route("/profile/", methods=["GET","POST"])
@login_required
def profile():
    email, user_name = None, None
    form = UpdateUser()
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == "POST":
        if form.validate_on_submit():
            user_name = form.user_name.data
            email = form.email.data
            email_exist = User.query.filter_by(email=form.email.data).first()
            user_name_exist = User.query.filter_by(user_name=form.user_name.data).first()
            if user_name and not email:
                if not user_name_exist:
                    user.user_name = user_name
                    db.session.commit()
                    flash(message="username changed successfuly", category="success")
                else:
                    flash("username already exists.", category="warning")
                    return redirect(url_for("profile"))
            elif email and not user_name:
                if not email_exist:
                    user.email = email
                    db.session.commit()
                    flash(message="email changed successfuly", category="success")
                else:
                    flash("email already exists.", category="warning")
                    return redirect(url_for("profile"))
            elif email and user_name:
                if not user_name_exist and not email_exist:
                    user.user_name = user_name
                    user.email = email
                    db.session.commit()
                    flash(message="username and email changed successfuly", category="success")
                else:
                    flash("user already exists.", category="warning")
                    return redirect(url_for("profile"))
            else:
                flash("the field is empty", category="warning")
                return redirect(url_for("profile"))
        else:
            flash("Invalid input", category="warning")
            return redirect(url_for("profile"))

    
    return render_template("profile.html",
            user = user,
            form = form,
        )


@app.route("/logout/", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash(message="You have been logged out!", category="info")
    return redirect(url_for("login"))

@app.route("/delete_account/", methods=["GET","POST"])
@login_required
def delete_account():
    user = User.query.filter_by(id=current_user.id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("signup"))


@app.route("/users/")
def users():
    users = User.query.all()
    return render_template("users.html",
            users = users,
    )


@app.route("/posts/", methods=["GET","POST"])
@login_required
def posts():
    form = PostForm()
    user = User.query.filter_by(id=current_user.id).first()
    all_posts = Post.query.all()
    if request.method == "POST":
        if form.validate_on_submit():
            post = Post(text=form.text.data, user_id=user.id)
            db.session.add(post)
            db.session.commit()
            flash(message="posted successfuly", category="success")
            return redirect(url_for("posts"))
    return render_template("posts.html",
        form = form,
        all_posts = all_posts,
    )

@app.route("/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
    form = PostForm()
    post = Post.query.get(post_id)
    if post.user_id == current_user.id:
        db.session.delete(post)
        db.session.commit()
        flash(message="the post has been deleted", category="success")
        return redirect(url_for("posts"))
    return render_template("posts.html",
        form = form
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500