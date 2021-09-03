import os
from unittest import TestCase

from models import db, User, Freetime, Task
from forms import CreateUserForm, LoginUserForm

os.environ["DATABASE_URL"] = "postgresql:///instime_test"

from app import app
from flask_login import current_user

app.config["WTF_CSRF_ENABLED"] = False
app.config["TESTING"] = True

db.drop_all()
db.create_all()

class RoutesTestCase(TestCase):
    """do get & post request work along with authorized views"""

    def setUp(self):
        """empty out old data & create some sample data"""

        User.query.delete()
        Freetime.query.delete()
        Task.query.delete()

        self.client = app.test_client()
        self.request_ctx = app.test_request_context

        with self.request_ctx():
            user = User.register("user@email.com", "strongpassword123", "Martin Brown")
            db.session.commit()
            data = {"email": "user@email.com", "password": "strongpassword123"}
            form = LoginUserForm(data=data)
            self.client.post("/login", data=form.data, follow_redirects=True)

        self.user = user
    
    def tearDown(self):
        """clean up the session"""

        db.session.rollback()
    
    def test_register(self):
        """does the register route work"""

        resp = self.client.get("/register")

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Register", str(resp.data))

        with self.request_ctx():
            data = {"name": "Susan Smith", "email": "kasj@agkj.com", "password": "sakgtj3lkqjtka"}
            form = CreateUserForm(data=data)
            resp = self.client.post("/register", data=form.data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Susan Smith", str(resp.data))

    def test_login(self):
        """does the login route work"""

        resp = self.client.get("/login")

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Login", str(resp.data))

        with self.request_ctx():
            data = {"email": "user@email.com", "password": "strongpassword123"}
            form = LoginUserForm(data=data)
            resp = self.client.post("/login", data=form.data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Martin Brown", str(resp.data))
            self.assertIsNotNone(User.query.filter_by(email = "user@email.com"))

    def test_logout(self):
        """does the logout route work"""

        resp = self.client.post("/logout", follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Hello Stranger", str(resp.data))
    
    def test_home_page(self):
        """does the home_page route work"""

        resp = self.client.get("/")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Martin Brown", str(resp.data))
    
    def test_freetimes_view(self):
        """does the freetimes_view route work"""

        resp = self.client.get("/times")

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Available times", str(resp.data))
    
    def test_tasks_view(self):
        """does the tasks_view route work"""

        resp = self.client.get("/tasks")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Add new task", str(resp.data))
    
    def test_update_task(self):
        """does the update_task route work"""

        task = Task(title="aklgn", description="lakjgka", user_id=self.user.id)
        db.session.add(task)
        db.session.commit()

        with self.request_ctx():
            resp = self.client.get(f"/tasks/{task.id}/edit")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Edit your task", str(resp.data))
    
    def test_plans_view(self):
        """does the plans_view route work"""

        resp = self.client.get("/plans")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Your plans", str(resp.data))

class LoginRequiredViewsTestCase(TestCase):
    """do the protected views all redirect to login"""

    def setUp(self):
        """set useful data on self"""

        self.client = app.test_client()
        self.request_ctx = app.test_request_context
    
    def test_logout(self):
        """does logout go to login"""

        with self.request_ctx():
            resp = self.client.post("/logout", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
    
    def test_freetimes_view(self):
        """does freetimes_view go to login"""

        with self.request_ctx():
            resp = self.client.get("/times", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
    
    def test_get_freetime(self):
        """does get_freetime go to login"""

        with self.request_ctx():
            resp = self.client.get("/times/1", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
    
    def test_tasks_view(self):
        """does tasks_view go to login"""

        with self.request_ctx():
            resp = self.client.get("/tasks", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
    
    def test_delete_task(self):
        """does tasks_view go to login"""

        with self.request_ctx():
            resp = self.client.delete("/tasks/1", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
    
    def test_update_task(self):
        """does update_task go to login"""

        with self.request_ctx():
            resp = self.client.get("/tasks/1/edit", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
    
    def test_plans_view(self):
        """does plans_view go to login"""

        with self.request_ctx():
            resp = self.client.get("/plans", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login", str(resp.data))
            self.assertFalse(current_user.is_authenticated)
