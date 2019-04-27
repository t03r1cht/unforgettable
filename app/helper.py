from app import db
from app.models import ReminderCategory, AppInfo, Settings, User
from datetime import datetime
import pytz


def get_categories():
    # TODO Order by descending category id so "Default" will be the default selected category
    reminder_categories = ReminderCategory.query.all()
    rc = [(str(cat.id), cat.name) for cat in reminder_categories]
    return rc


def get_local_time(utc_dt):
    selected_timezone = Settings.query.filter_by(
        key="timezone").first().value or "America/New_York"
    local_tz = pytz.timezone(selected_timezone)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def get_supported_timezones():
    return [(i, i) for i in pytz.common_timezones]


def require_admin_account_creation():
    # Check if an admin account has already been created
    registered_users = User.query.all()
    force_admin_creation = False
    if len(registered_users) == 0 or registered_users == []:
        # No users have been created yet, prompt for creation of admin user
        force_admin_creation = True
    else:
        admin_exists = False
        for user in registered_users:
            if user.is_admin:
                admin_exists = True
                break
        if not admin_exists:
            # No admin users have been created yet, prompt for creation of admin user
            force_admin_creation = True
    return force_admin_creation
