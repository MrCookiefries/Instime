from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin
import dateutil.parser as dt
from flask_cors import CORS
from requests import get
import os

from models import db, connect_db, User, Task, Freetime, blocks
from forms import CreateUserForm, LoginUserForm, UserTaskForm

# ***********************************************************************
# APP CONFIGURATIONS

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgres:///instime").replace("postgres", "postgresql")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "p-olIJg0C1yu1oUqaccDgztpWa-J1Ag0")

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
        user = User.register(email=email, password=password, name=name)
        db.session.commit()
        login_user(user, True)
        flash("Successfully created account.", "success")
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
            flash("Successfully logged into your account.", "success")
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
    flash("Successfully logged out.", "success")
    return redirect(url_for("home_page"))

# ***********************************************************************
# HOME PAGE

@app.route("/")
def home_page():
    """shows the home page"""
    return render_template("index.html", action="view")

@app.route("/quotes")
def get_quotes():
    """attempts to get quotes"""
    try:
        quotes = get("https://goquotes-api.herokuapp.com/api/v1/all/quotes")
        return jsonify(quotes.json())
    except Exception as err:
        return jsonify(error=err), 500

# ***********************************************************************
# TIMES VIEWS

@app.route("/times", methods=["GET", "POST", "PATCH", "DELETE"])
@login_required
def freetimes_view():
    """shows times management for user"""
    if request.method == "GET":
        freetimes = current_user.freetimes
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
            flash("Successfully added your new freetime.", "success")
            return jsonify(url=url_for("freetimes_view"))
        return jsonify(error="required data not provided (start/end) times")

    freetime_id = request.json.get("id")
    if freetime_id:
        freetime = Freetime.query.get(freetime_id)
        if freetime and freetime.user_id == current_user.id:

            if request.method == "DELETE":
                db.session.delete(freetime)
                db.session.commit()
                flash("Successfully deleted your freetime.", "success")
                return jsonify(url=url_for("freetimes_view"))

            start_time = request.json.get("start")
            end_time = request.json.get("end")
            if start_time and end_time:
                start_time = dt.parse(start_time).isoformat()
                end_time = dt.parse(end_time).isoformat()
                freetime.start_time = start_time
                freetime.end_time = end_time
                db.session.commit()
                flash("Successfully updated your freetime.", "success")
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

# ***********************************************************************
# TASKS PAGE VIEWS

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks_view():
    """shows task management for user"""
    form = UserTaskForm()
    sort = request.args.get("sort")
    if sort:
        tasks = Task.get_user_tasks_by_sort(current_user, sort)
    else:
        tasks = current_user.tasks
    form.freetimes.choices = [(f.id, f"{f.pretty_start} - {f.pretty_end}") for f in current_user.freetimes]
    if form.validate_on_submit():
        task = Task()
        freetimes = form.freetimes.data
        form.__delitem__("freetimes")
        form.populate_obj(task)
        task.user_id = current_user.id
        task_freetimes = []
        for freetime_id in freetimes:
            freetime = Freetime.query.get(freetime_id)
            if not freetime:
                flash("Oh no, no freetime was found in our database.", "danger")
            elif freetime.user_id != current_user.id:
                flash("You don't own that freetime and can't assign tasks to it.", "danger")
            else:
                task_freetimes.append(freetime)
        task.freetimes = task_freetimes
        db.session.add(task)
        db.session.commit()
        flash("Successfully created your task.", "success")
        return redirect(url_for("tasks_view"))
    return render_template("user/tasks.html", tasks=tasks, form=form, submit="Add")

@app.route("/tasks/<int:id>", methods=["DELETE"])
@login_required
def delete_task(id):
    """deletes a given user's task"""
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return jsonify(error="must provide the (id) of a task the user owns")
    db.session.delete(task)
    db.session.commit()
    flash("Successfully deleted your task.", "success")
    return jsonify(url=url_for("tasks_view"))

@app.route("/tasks/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update_task(id):
    """updates a user's task"""
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash("You must own the task to edit it.", "warning")
        return redirect(url_for("tasks_view"))
    form = UserTaskForm(obj=task)
    form.freetimes.choices = [(f.id, f"{f.pretty_start} - {f.pretty_end}") for f in current_user.freetimes]
    if form.validate_on_submit():
        freetimes = form.freetimes.data
        form.__delitem__("freetimes")
        form.populate_obj(task)
        task_freetimes = []
        for freetime_id in freetimes:
            freetime = Freetime.query.get(freetime_id)
            if not freetime:
                flash("Oh no, no freetime was found in our database.", "danger")
            elif freetime.user_id != current_user.id:
                flash("You don't own that freetime and can't assign tasks to it.", "danger")
            else:
                task_freetimes.append(freetime)
        task.freetimes = task_freetimes
        db.session.commit()
        flash("Successfully updated your task.", "success")
        next = request.args.get("next")
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for("tasks_view"))
    if request.method == "GET":
        form.freetimes.data = [f.id for f in task.freetimes]
    return render_template("user/edit-task.html", form=form, submit="Save")

# ***********************************************************************
# PLANS PAGE VIEWS

@app.route("/plans")
@login_required
def plans_view():
    """shows block management to user"""
    plans = (db.session.query(blocks, Task, Freetime, User)
        .join(Task, Task.id == blocks.c.task_id)
        .join(Freetime, Freetime.id == blocks.c.freetime_id)
        .join(User, Task.user_id == User.id)
        .filter(User.id == current_user.id)
        .order_by(Freetime.start_time, Freetime.end_time)
    ).all()

    user_blocks = [(plan[2], plan[3]) for plan in plans]

    open_tasks = [task for task in current_user.tasks if task not in [ub[0] for ub in user_blocks]]
    open_freetimes = [freetime for freetime in current_user.freetimes if freetime not in [ub[1] for ub in user_blocks]]

    return render_template(
        "user/plans.html", blocks=user_blocks,
        open_tasks=open_tasks, open_freetimes=open_freetimes,
    )
