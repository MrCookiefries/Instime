from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory

from models import db, User, Task

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class CreateUserForm(ModelForm):
    """form for making users"""
    class Meta:
        model = User

class LoginUserForm(ModelForm):
    """form for logging in users"""
    class Meta:
        model = User
        only = ["email", "password"]
        unique_validator = None
