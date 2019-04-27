from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from app.models import ReminderCategory


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired()])
    is_admin = HiddenField("admin", validators=[
                           DataRequired()], default="0")
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class AddReminderForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField(
        "Description", widget=TextArea(), validators=[DataRequired()])
    category = SelectField("Category")
    submit = SubmitField("Add")


class AddReminderCategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired()])
    submit = SubmitField("Add")


class SettingsSelectTimezoneForm(FlaskForm):
    timezone = SelectField("Timezone", default="Europe/Berlin")
    submit = SubmitField("Save")


class EditReminderForm(FlaskForm):
    title = StringField("Title", widget=TextArea(),
                        validators=[DataRequired()])
    description = StringField("Description", widget=TextArea())
    category = SelectField("Category")
    submit = SubmitField("Save")
