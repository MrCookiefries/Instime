from wtforms import widgets
from flask_wtf import FlaskForm
from wtforms.fields.core import SelectMultipleField
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

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class UserTaskForm(ModelForm):
    """form for creating / editing tasks of users"""
    class Meta:
        model = Task
    
    freetimes = MultiCheckboxField("Freetimes", coerce=int)
