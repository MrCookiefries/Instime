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

    tasks = db.relationship("Task", backref="user")
    freetimes = db.relationship("Freetime", backref="user")

    def __repr__(self):
        return f"<User #{self.id} {self.name} - {self.email}>"
    
    @classmethod
    def register(cls, email, password, name):
        """creates new user instance with encryped password"""
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = cls(email=email, name=name, password=hashed_password)
        db.session.add(new_user)
        return new_user
    
    @classmethod
    def authenticate(cls, email, password):
        """checks if user exists with credentials"""
        user = cls.query.filter_by(email = email).one_or_none()
        if user:
            correct_password = bcrypt.check_password_hash(user.password, password)
            if correct_password:
                return user
        return False

blocks = db.Table(
    "blocks",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id", ondelete="cascade"), primary_key=True),
    db.Column("freetime_id", db.Integer, db.ForeignKey("freetimes.id", ondelete="cascade"), primary_key=True)
)

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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)

    freetimes = db.relationship("Freetime", secondary=blocks, backref="tasks")

    def __repr__(self):
        return f"<Task #{self.id} {self.title} ({self.status}) user_id={self.user_id}>"
    
    @property
    def pretty_estimate(self):
        total = self.time_estimate
        if not total: return
        minutes = total % 60
        hours = (total - minutes) / 60
        return f"{int(hours)} hours & {minutes} minutes"
    
    @classmethod
    def get_user_tasks_by_sort(cls, user, sort):
        """returns tasks by user in a sorted fashion"""
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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)

    def __repr__(self):
        return f"<Freetime #{self.id} start={self.start_time} end={self.end_time} user_id={self.user_id}>"
    
    @property
    def pretty_start(self):
        utc = self.start_time.replace(tzinfo=tz.tzutc())
        return utc.astimezone(tz.tzlocal()).strftime("%b %d, %Y @ %H:%M")
    
    @property
    def pretty_end(self):
        utc = self.end_time.replace(tzinfo=tz.tzutc())
        return utc.astimezone(tz.tzlocal()).strftime("%b %d, %Y @ %H:%M")
