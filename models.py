from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy_utils import EmailType
from wtforms.fields.simple import PasswordField, TextAreaField
from dateutil import tz
from sqlalchemy import nullslast

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """connects app to database"""
    db.app = app
    db.init_app(app)

class User(UserMixin, db.Model):
    """model for users"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(EmailType, unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False, info={"form_field_class": PasswordField})
    # relationship for a users tasks & freetimes
    tasks = db.relationship("Task", backref="user") 
    freetimes = db.relationship("Freetime", backref="user")

    def __repr__(self):
        return f"<User #{self.id} {self.name} - {self.email}>"
    
    @classmethod
    def register(cls, email, password, name):
        """creates new user instance with encryped password

        Args:
            email (string): user's email address
            password (password): user's password to log in
            name (string): user's name to greet them with

        Returns:
            User: instance of the User class made from the args passed
        """
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = cls(email=email, name=name, password=hashed_password)
        db.session.add(new_user)
        return new_user
    
    @classmethod
    def authenticate(cls, email, password):
        """checks if credentials are correct for a user account

        Args:
            email (string): user's email address
            password (string): user's password to log in

        Returns:
            User | False: if they exist, the user account, else false
        """
        user = cls.query.filter_by(email = email).one_or_none()
        if user:
            correct_password = bcrypt.check_password_hash(user.password, password)
            if correct_password:
                return user
        return False

# a join table for the many to many realtionship of tasks to freetimes & freetimes to tasks
blocks = db.Table(
    "blocks",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id", ondelete="cascade"), primary_key=True),
    db.Column("freetime_id", db.Integer, db.ForeignKey("freetimes.id", ondelete="cascade"), primary_key=True)
)

# used as the only values for the status of a task
STATUSES = ("pending", "partial", "done")

class Task(db.Model):
    """model for tasks"""
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(250), nullable=False, info={"form_field_class": TextAreaField})
    status = db.Column(db.String(10), nullable=False, default=STATUSES[0], info={
        'choices': [(s, s.title()) for s in STATUSES]
    })
    time_estimate = db.Column(db.Integer, info={
        'label': 'time estimate (minutes)',
        "min": 1
    })
    priority = db.Column(db.Integer, nullable=False, default=0, info={
        'choices': [(i, i) for i in range(10)],
        "label": "priority (0 low - 9 high)"
    })
    # links a user to a task, tasks must have a user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    # relationship for task to have many freetimes & for freetime to have many tasks
    freetimes = db.relationship("Freetime", secondary=blocks, backref="tasks")

    def __repr__(self):
        return f"<Task #{self.id} {self.title} ({self.status}) user_id={self.user_id}>"
    
    @property
    def pretty_estimate(self):
        """uses the time estimate (minutes) & gives back the time in hours & minutes

        Returns:
            string | None: if time estimate is not null, the formatted string of time, else None
        """
        total = self.time_estimate
        if not total: return
        minutes = total % 60
        hours = (total - minutes) / 60
        return f"{int(hours)} hours & {minutes} minutes"
    
    @classmethod
    def get_user_tasks_by_sort(cls, user, sort):
        """returns tasks by user in a sorted fashion

        Args:
            user (User): the user to get tasks from
            sort (string): "status", "priority", or other value to sort the tasks order by

        Returns:
            SQLAlchemy Query object: used to get a list of tasks from a user on a specific sort
        """
        query = cls.query.filter(cls.user_id == user.id)
        if sort == "status":
            return query.order_by(cls.status, cls.priority.desc()).all()
        if sort == "priority":
            return query.order_by(cls.priority.desc(), nullslast(cls.time_estimate.desc()))
        return query.order_by(nullslast(cls.time_estimate.desc()), cls.priority.desc())

class Freetime(db.Model):
    """model for freetimes"""
    __tablename__ = "freetimes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    # links freetime to a user, freetimes must have a user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)

    def __repr__(self):
        return f"<Freetime #{self.id} start={self.start_time} end={self.end_time} user_id={self.user_id}>"
    
    @property
    def pretty_start(self):
        """formats the start_time into a display date

        Returns:
            string: nicely formatted date
        """
        utc = self.start_time.replace(tzinfo=tz.tzutc())
        return utc.astimezone(tz.tzlocal()).strftime("%b %d, %Y @ %H:%M")
    
    @property
    def pretty_end(self):
        """formats the end_time into a display date

        Returns:
            string: nicely formatted date
        """
        utc = self.end_time.replace(tzinfo=tz.tzutc())
        return utc.astimezone(tz.tzlocal()).strftime("%b %d, %Y @ %H:%M")
