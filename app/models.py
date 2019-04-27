from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login


# Create the migration repository (goal: if there are changes to the database scheme, flask-migrate will migrate it easily
# - Create migration repository: .\venv\Scripts\python.exe -m flask db init
# - Create migration script (so we have the script to migrate at any point in time to the new database scheme):
#   .\venv\Scripts\python.exe -m flask db migrate -m "migration text"
# - Apply the database migration script: .\venv\Scripts\python.exe -m flask db upgrade
#
# More information https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database at
# "Database Upgrade and Downgrade Workflow"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    reg_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reminders = db.relationship("Reminder", backref="author", lazy="dynamic")
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True)
    description = db.Column(db.String(500))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    finish_date = db.Column(db.DateTime, index=True)
    finished = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        "reminder_category.id"), nullable=False)

    def __repr__(self):
        return '<Reminder {}>'.format(self.title)


class ReminderCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    reminders = db.relationship("Reminder", backref="category", lazy="dynamic")

    def __repr__(self):
        return '<ReminderCategory {}>'.format(self.name)


class AppInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), index=True, unique=True)
    value = db.Column(db.String(500), index=True)

    def __repr__(self):
        return '<AppInfo {}>'.format(self.key)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), index=True, unique=True)
    value = db.Column(db.String(500), index=True)

    def __repr__(self):
        return '<Settings {}>'.format(self.key)
