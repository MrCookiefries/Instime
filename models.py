from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy_utils import EmailType, PasswordType

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
    password = db.Column(PasswordType(schemes=["bcrypt"]), nullable=False)

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
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True),
    db.Column("freetime_id", db.Integer, db.ForeignKey("freetimes.id"), primary_key=True)
)

class Task(db.Model):
    """model for tasks"""
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(10), nullable=False, default="Pending") # "pending" "planned" "done"
    time_estimate = db.Column(db.Integer) # null means they don't know
    priority = db.Column(db.Integer, nullable=False, default=0) # 0-9 (low-high)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    freetimes = db.relationship("Freetime", secondary=blocks, backref="tasks")

    def __repr__(self):
        return f"<Task #{self.id} {self.title} ({self.status}) user_id={self.user_id}>"

class Freetime(db.Model):
    """model for freetimes"""
    __tablename__ = "freetimes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Freetime #{self.id} start={self.start_time} end={self.end_time} user_id={self.user_id}>"
