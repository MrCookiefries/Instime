from datetime import datetime
from flask import Flask, json, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin
import dateutil.parser as dt
from flask_cors import CORS

from models import db, connect_db, User, Task, Freetime
from secret import SECRET_KEY
from forms import CreateUserForm, LoginUserForm

# ***********************************************************************
# APP CONFIGURATIONS

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///instime"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET_KEY

CORS(app)
login_manager = LoginManager()
connect_db(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "You must be logged in to access that."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ***********************************************************************
# HELPER URL FUNCTIONS

# https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work
# Function below adopted from ^ on August 27th, 2021
def is_safe_url(target):
    """checks if url's redirect target leads to the same server"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

# ***********************************************************************
# USER REGISTER / LOGIN / LOGOUT

@app.route("/register", methods=["GET", "POST"])
def register():
    """registers a new user"""
    form = CreateUserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # will fail if duplicate emails exist
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
    return render_template("sign-in.html", form=form, submit="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    """logs in a user"""
    form = LoginUserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.authenticate(email, password)
        if not user:
            form.email.errors.append("Email or Password is incorrect.")
        else:
            login_user(user, True)
            flash("Successfully logged into your account.", "info")
            next = request.args.get("next")
            if not is_safe_url(next):
                return abort(400)
            return redirect(next or url_for("home_page"))
    return render_template("sign-in.html", form=form, submit="Login")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """logs a user out"""
    logout_user()
    flash("Successfully logged out.", "info")
    return redirect(url_for("home_page"))

# ***********************************************************************
# MAIN PAGE VIEWS

@app.route("/")
def home_page():
    """shows the home page"""
    return render_template("index.html", action="view")

@app.route("/times", methods=["GET", "POST", "PATCH", "DELETE"])
@login_required
def freetimes_view():
    """shows times management for user"""
    if request.method == "GET":
        freetimes = Freetime.query.filter(Freetime.user_id == current_user.id).all()
        return render_template("user/times.html", freetimes=freetimes)

    elif request.method == "POST":
        start_time = request.json.get("start")
        end_time = request.json.get("end")
        if start_time and end_time:
            start_time = dt.parse(start_time).isoformat()
            end_time = dt.parse(end_time).isoformat()
            freetime = Freetime(start_time=start_time, end_time=end_time, user_id=current_user.id)
            db.session.add(freetime)
            db.session.commit()
            flash("Successfully added your new freetime.", "info")
            return jsonify(url=url_for("freetimes_view"))
        return jsonify(error="required data not provided (start/end) times")

    freetime_id = request.json.get("id")
    if freetime_id:
        freetime = Freetime.query.get(freetime_id)
        if freetime and freetime.user_id == current_user.id:

            if request.method == "DELETE":
                db.session.delete(freetime)
                db.session.commit()
                flash("Successfully deleted your freetime.", "info")
                return jsonify(url=url_for("freetimes_view"))

            start_time = request.json.get("start")
            end_time = request.json.get("end")
            if start_time and end_time:
                start_time = dt.parse(start_time).isoformat()
                end_time = dt.parse(end_time).isoformat()
                freetime.start_time = start_time
                freetime.end_time = end_time
                db.session.commit()
                flash("Successfully updated your freetime.", "info")
                return jsonify(url=url_for("freetimes_view"))

        if request.method == "DELETE":
            return jsonify(error="must provide the (id) of a freetime the user owns")

        return jsonify(error="must provide the (id) of a freetime the user owns & the (start/end) times")

@app.route("/times/<int:id>")
@login_required
def get_freetime(id):
    """gets a specific freetime if exists"""
    freetime = Freetime.query.get(id)
    if freetime and freetime.user_id == current_user.id:
        return jsonify(start=freetime.start_time, end=freetime.end_time)
    return jsonify(error="requires (id) of freetime and must belong to the user")


