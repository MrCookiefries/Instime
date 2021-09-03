import os
from unittest import TestCase
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from flask_bcrypt import Bcrypt

from models import db, User, Freetime, Task

os.environ['DATABASE_URL'] = "postgresql:///instime_test"

from app import app

app.config["TESTING"] = True

db.drop_all()
db.create_all()

bcrypt = Bcrypt()

class UserModelTestCase(TestCase):
    """does the user model behave right"""

    def setUp(self):
        """clear out old data and create some sample data"""

        Freetime.query.delete()
        Task.query.delete()
        User.query.delete()

        hashed_password = bcrypt.generate_password_hash("strongpassword123").decode("utf-8")
        user = User(email="user@email.com", password=hashed_password, name="Martin Brown")
        db.session.add(user)
        db.session.commit()

        self.user = user
    
    def tearDown(self):
        """clean out the session"""

        db.session.rollback()
    
    def add_second_user(self):
        """adds a second user and returns the user"""

        user = User(email="test@mail.net", name="aksjga", password="j3h6na3kamg")
        db.session.add(user)
        db.session.commit()

        return user
    
    def add_user_task(self):
        """adds a task to the user on self and returns the task"""

        task = Task(title="walk the dog", description="sagkjlaksg", user_id=self.user.id)
        db.session.add(task)
        db.session.commit()

        return task
    
    def add_user_freetime(self):
        """adds a freetime to the user on self and returns the freetime"""

        freetime = Freetime(start_time=datetime.now(), end_time=datetime.now(), user_id=self.user.id)
        db.session.add(freetime)
        db.session.commit()

        return freetime

    def test_user_model(self):
        """does the basic model work"""

        user = self.add_second_user()

        self.assertEqual(len(user.tasks), 0)
        self.assertEqual(len(user.freetimes), 0)
        self.assertIsInstance(user.id, int)
    
    def test_user_repr(self):
        """does the repr method work right"""

        user = self.user
        repr = user.__repr__()

        self.assertIn(str(user.id), repr)
        self.assertIn(user.email, repr)
        self.assertIn(user.name, repr)
    
    def test_user_tasks(self):
        """does the tasks relationship work for user"""

        self.assertEqual(len(self.user.tasks), 0)

        task = self.add_user_task()

        self.assertEqual(len(self.user.tasks), 1)
        self.assertIsInstance(self.user.tasks[0], Task)
        self.assertEqual(self.user.tasks[0], task)
    
    def test_user_freetimes(self):
        """does the freetimes relationship work for user"""

        self.assertEqual(len(self.user.freetimes), 0)

        freetime = self.add_user_freetime()

        self.assertEqual(len(self.user.freetimes), 1)
        self.assertIsInstance(self.user.freetimes[0], Freetime)
        self.assertEqual(self.user.freetimes[0], freetime)

    def test_user_register(self):
        """does the user register method work right"""

        user = User.register("search@mail.net", password="2jhk6eo8fvsa", name="gklajlag")
        db.session.commit()

        self.assertIsInstance(user, User)
    
    def test_user_register_fail(self):
        """does the user register method fail upon duplicate emails"""

        user = User.register(self.user.email, password="2jhk6eo8fvsa", name="gklajlag")

        self.assertIsInstance(user, User)
        self.assertRaises((UniqueViolation, IntegrityError), db.session.commit)
    
    def test_user_authenticate(self):
        """does the user authenticate method work right"""

        user = User.authenticate(self.user.email, "strongpassword123")

        self.assertIsInstance(user, User)
        self.assertEqual(user, self.user)
    
    def test_user_authenticate_fail(self):
        """does the user authenticate work right when there is wrong credentials"""

        wrong_password = User.authenticate(self.user.email, "sakjhtkj3jq")
        wrong_email = User.authenticate("ka53@agk.com", self.user.password)
        wrong_credentials = User.authenticate("ak@sadg.com", "asjhgk3ljqkgea")

        self.assertFalse(wrong_password)
        self.assertFalse(wrong_email)
        self.assertFalse(wrong_credentials)

class TaskModelTestCase(TestCase):
    """does the task model behave right"""

    def setUp(self):
        """clear out old data and create some sample data"""

        Freetime.query.delete()
        Task.query.delete()
        User.query.delete()

        hashed_password = bcrypt.generate_password_hash("strongpassword123").decode("utf-8")
        user = User(email="user@email.com", password=hashed_password, name="Martin Brown")
        db.session.add(user)
        db.session.commit()
        task = Task(title="walk dog", description="walk the dog", user_id=user.id)
        db.session.add(task)
        db.session.commit()

        self.user = user
        self.task = task
    
    def tearDown(self):
        """clean out the session"""

        db.session.rollback()
    
    def add_user_freetime(self):
        """adds a freetime to the user on self and returns the freetime"""

        freetime = Freetime(start_time=datetime.now(), end_time=datetime.now(), user_id=self.user.id)
        db.session.add(freetime)
        db.session.commit()

        return freetime
    
    def test_task_model(self):
        """does the basic task model work"""

        task = Task(title="sajgkl", description="sakjtgk3a", user_id=self.user.id)
        db.session.add(task)
        db.session.commit()

        self.assertIsInstance(task, Task)
        self.assertIsInstance(task.id, int)
        self.assertTrue(task.status)
        self.assertIsNone(task.time_estimate)
        self.assertEqual(task.priority, 0)
    
    def test_task_user(self):
        """does the user realationship work for task"""

        user = self.task.user

        self.assertIsInstance(user, User)
        self.assertEqual(user, self.user)
    
    def test_task_freetimes(self):
        """does the freetimes relationship work for task"""

        self.assertEqual(len(self.task.freetimes), 0)

        freetime = self.add_user_freetime()
        self.task.freetimes.append(freetime)
        db.session.commit()

        self.assertEqual(len(self.task.freetimes), 1)
        self.assertIsInstance(self.task.freetimes[0], Freetime)
    
    def test_task_repr(self):
        """does the repr method work on task"""

        task = self.task
        repr = task.__repr__()

        self.assertIn(str(task.id), repr)
        self.assertIn(task.title, repr)
        self.assertIn(task.status, repr)
        self.assertIn(str(task.user_id), repr)
    
    def test_task_pretty_estimate(self):
        """does the pretty_estimate property work on task"""

        task = Task(title="sakgjh", description="sakjhga", time_estimate=222, user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        pretty_estimate = task.pretty_estimate

        self.assertIsNotNone(pretty_estimate)
        self.assertIn("3 hours", pretty_estimate)
        self.assertIn("42 minutes", pretty_estimate)
    
    def test_task_pretty_estimate_no_time(self):
        """does the pretty estimate property work right when there is no time estimate"""

        task = Task(title="akljhae", description="aehu3nahedsrj", user_id=self.user.id)
        db.session.add(task)
        db.session.commit()

        self.assertIsNone(task.pretty_estimate)

class FreetimeModelTestCase(TestCase):
    """does the freetime model behave right"""

    def setUp(self):
        """clear out old data and create some sample data"""

        Freetime.query.delete()
        Task.query.delete()
        User.query.delete()

        hashed_password = bcrypt.generate_password_hash("strongpassword123").decode("utf-8")
        user = User(email="user@email.com", password=hashed_password, name="Martin Brown")
        db.session.add(user)
        db.session.commit()
        freetime = Freetime(start_time=datetime.now(), end_time=datetime.now(), user_id=user.id)
        db.session.add(freetime)
        db.session.commit()

        self.user = user
        self.freetime = freetime
    
    def tearDown(self):
        """clean out the session"""

        db.session.rollback()
    
    def add_user_task(self):
        """adds a task to the user on self and returns the task"""

        task = Task(title="walk the dog", description="sagkjlaksg", user_id=self.user.id)
        db.session.add(task)
        db.session.commit()

        return task
    
    def test_freetime_model(self):
        """does the basic model work"""

        freetime = Freetime(start_time=datetime.now(), end_time=datetime.now(), user_id=self.user.id)
        db.session.add(freetime)
        db.session.commit()

        self.assertIsInstance(freetime, Freetime)
        self.assertIsInstance(freetime.id, int)
        self.assertIsInstance(freetime.user_id, int)
    
    def test_freetime_repr(self):
        """does the repr method work on freetime"""

        freetime = self.freetime
        repr = freetime.__repr__()

        self.assertIn(str(freetime.id), repr)
        self.assertIn(str(freetime.start_time), repr)
        self.assertIn(str(freetime.end_time), repr)
        self.assertIn(str(freetime.user_id), repr)
    
    def test_freetime_user(self):
        """does the user relationship work on freetime"""

        freetime = self.freetime
        user = self.user

        self.assertEqual(freetime.user_id, user.id)
        self.assertIsInstance(freetime.user, User)
        self.assertEqual(user, freetime.user)
    
    def test_freetime_tasks(self):
        """does the tasks realtionship work on freetime"""

        self.assertEqual(len(self.freetime.tasks), 0)

        task = self.add_user_task()
        freetime = self.freetime
        freetime.tasks.append(task)
        db.session.commit()

        self.assertEqual(len(freetime.tasks), 1)
        self.assertIsInstance(freetime.tasks[0], Task)
