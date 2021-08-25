from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from is_safe_url import is_safe_url

from models import db, connect_db, User, Task, Freetime
from secret import SECRET_KEY
from forms import CreateUserForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///instime"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET_KEY

login_manager = LoginManager()
connect_db(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "You must be logged in to access that."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
    """registers a new user"""
    form = CreateUserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = User.register(email=email, password=password, name=name)
        db.session.commit()
        login_user(user, True)
        flash("Successfully created account.", "info")
        # incase they try to access another page,
        # send them here with next as original page they tried to vist
        next = request.args.get("next")
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for("home_page"))
    return render_template("register.html", form=form, submit="Register")

@app.route("/")
def home_page():
    """shows the home page"""
    return render_template("index.html")

