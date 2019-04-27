import json
import os
import sqlite3
from datetime import datetime
import safe

from flask import (Response, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import (LoginManager, current_user, login_manager,
                         login_required, login_user, logout_user)
from pytz import common_timezones
from sqlalchemy import engine, exists

from app import app
from app.forms import (AddReminderCategoryForm, AddReminderForm,
                       EditReminderForm, LoginForm, SettingsSelectTimezoneForm, RegisterForm)
from app.helper import get_categories, get_local_time, get_supported_timezones, require_admin_account_creation
from app.models import AppInfo, Reminder, ReminderCategory, Settings, User, db


@app.login_manager.unauthorized_handler
def unauthorized():
    return render_template("errorpages/unauthorized.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errorpages/404.html")


@app.errorhandler(405)
def method_now_allowed(e):
    return render_template("errorpages/405.html")


@app.template_filter("locale_strftime")
def _jinja2_filter_locale_strftime(date, fmt=None):
    return get_local_time(date).strftime("%d/%m/%Y %H:%M")


@app.before_first_request
def init_app():
    app.logger.debug("Running pre-init...")
    overwrite_init_db = False
    app_version = "0.1"
    if not AppInfo.query.all() or not Settings.query.all() or overwrite_init_db:
        db.session.add(AppInfo(key="app_version", value=app_version))
        launch_date = str(datetime.utcnow())
        db.session.add(AppInfo(key="first_launch_date", value=launch_date))
        app.logger.debug("First launch date set to: %s", launch_date)
        default_timezone = "America/New_York"
        db.session.add(Settings(key="timezone", value=default_timezone))
        app.logger.debug("Default timezone set to: %s" % default_timezone)
        db.session.commit()
        app.logger.debug("Database initialized")
    else:
        app.logger.debug("Database already initialized (%s)" % app_version)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("start"))
    login_form = LoginForm()
    if request.method == "POST":
        if login_form.validate_on_submit():
            user = User.query.filter_by(
                username=login_form.username.data).first()
            if user is None or not user.check_password(login_form.password.data):
                flash("Username and/or password incorrect.", "error")
                return redirect(url_for("login"))
            login_user(user, remember=login_form.remember_me.data)
            flash("You have successfully logged in. Welcome back!", "success")
            return redirect(url_for("start"))
        return redirect(url_for("login"))
    else:
        return render_template("login.html", form=login_form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    signup_form = RegisterForm()
    force_admin_creation = require_admin_account_creation()
    if request.method == "POST":
        if signup_form.validate_on_submit():
            username = signup_form.username.data
            password = signup_form.password.data
            password_confirm = signup_form.confirm_password.data
            is_admin = signup_form.is_admin.data

            if is_admin != "1" and is_admin != "0":
                flash("Please do not tamper with the form data.", "error")
                return redirect(url_for("signup"))
            else:
                # Convert the is_admin value to a bool value since it's easier to work with such values
                # is_admin = 0 = False
                # is_admin = 1 = True
                is_admin = bool(int(is_admin))
            # Check if an admin account is actually required (do not rely on passed hidden field value since it may have been tampered with)
            if is_admin and not force_admin_creation:
                flash("Please do not tamper with the form data (admin rights were requested although an admin account already exists).", "error")
                return redirect(url_for("signup"))
            if not username or not password or not password_confirm:
                flash("Please fill out every field.", "warning")
                return redirect(url_for("signup"))
            if password != password_confirm:
                flash("Password confirmation did not match your password.", "error")
                return redirect(url_for("signup"))
            forbidden_strength_lvl = []
            # Require special password strength when creating the admin account
            if is_admin:
                forbidden_strength_lvl.append("terrible")
                forbidden_strength_lvl.append("simple")
                forbidden_strength_lvl.append("medium")
            else:
                forbidden_strength_lvl.append("terrible")
                forbidden_strength_lvl.append("simple")

            pw_check = safe.check(password)
            app.logger.debug("strength: %s" % pw_check.strength)
            if pw_check.strength in forbidden_strength_lvl:
                flash("Password strength is: %s (reason: %s)." %
                      (pw_check.strength, pw_check.message), "error")
                return redirect(url_for("signup"))
            # Check if the username already exists
            dup = db.session.query(exists().where(
                User.username == username)).scalar()
            if dup:
                flash("User %s already exists." % username, "error")
                return redirect(url_for("signup"))
            new_user = User(username=username)
            new_user.set_password(password)
            # Set admin privileges depending on the hidden field
            new_user.is_admin = is_admin
            db.session.add(new_user)
            db.session.commit()
            flash("%s, your account has been successfully created." %
                  username, "success_signup")
            return redirect(url_for("signup"))
    else:
        if force_admin_creation:
            # Set the hidden field to 1 (we need this field to evaluate whether the account to be created is doing to be an admin)
            # We need the field create_admin to display the info message that the account to be created is going to be an admin account
            signup_form.is_admin.data = "1"
            return render_template("signup.html", form=signup_form, create_admin="1")
        else:
            # No need to set signup_form.is_admin.data since it defaults to 0 (no admin)
            return render_template("signup.html", form=signup_form, create_admin="0")


@app.route("/start")
@login_required
def start():
    addReminderForm = AddReminderForm()
    addReminderForm.category.choices = get_categories()
    addReminderCategoryForm = AddReminderCategoryForm()
    all_items = Reminder.query.filter_by(user_id=current_user.id, finished=False).order_by(
        Reminder.creation_date.desc()).all()
    all_categories = ReminderCategory.query.all()
    all_category_labels = {}
    for c in all_categories:
        all_category_labels[c.id] = c.name
    # Initialize empty lists
    all_items_grouped = {}
    for c_id, c_name in all_category_labels.items():
        all_items_grouped[c_id] = []
    for item in all_items:
        # TODO Convert timestamp to local time
        all_items_grouped[item.category.id].append(item)
    return render_template("start.html", addReminderForm=addReminderForm,
                           addReminderCategoryForm=addReminderCategoryForm, reminders=all_items_grouped,
                           category_labels=all_category_labels)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/test")
def test():
    flash("my-test-message", "success_signup")
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/addreminder", methods=["POST"])
@login_required
def add_reminder():
    form = AddReminderForm()
    form.category.choices = get_categories()
    if form.validate_on_submit():
        if not form.title.data or not form.category.data:
            flash("Fields cannot be empty.", "error")
            return redirect(url_for("start"))
        # Check if textarea is not longer than 500 chars
        if len(form.description.data) > 500:
            flash("Description character maximum is 500.", "error")
            return redirect(url_for("start"))
        # Check if a reminder item with the same title already exists
        # dup = db.session.query(exists().where(Reminder.title == form.title.data, Reminder.finished is False)).scalar()
        dup = current_user.reminders.filter_by(
            title=form.title.data, finished=False).first()
        if dup:
            flash("A reminder item with this name already exists", "error")
            return redirect(url_for("start"))
        # Check if the category is a valid one
        category_int = int(form.category.data)
        cat_exists = ReminderCategory.query.filter_by(id=category_int).first()
        if not cat_exists:
            flash("Invalid category", "error")
            return redirect(url_for("start"))
        reminder = Reminder(title=form.title.data, description=form.description.data, user_id=current_user.id,
                            category_id=category_int)
        db.session.add(reminder)
        db.session.commit()
        flash("New item was created.", "success")
        return redirect(url_for("start"))
    flash("Unable to create item.", "error")
    return redirect(url_for("start"))


@app.route("/addcategory", methods=["POST"])
@login_required
def add_category():
    form = AddReminderCategoryForm()
    if form.validate_on_submit():
        if not form.name.data:
            flash("Category name cannot be empty.", "error")
            return redirect(url_for("start"))
        dup = db.session.query(exists().where(
            ReminderCategory.name == form.name.data)).scalar()
        if dup:
            flash("A category with this name already exists", "error")
            return redirect(url_for("start"))
        reminder_category = ReminderCategory(name=form.name.data)
        db.session.add(reminder_category)
        db.session.commit()
        flash("New category was created.", "success")
        return redirect(url_for("start"))
    flash("Unable to create category.", "error")
    return redirect(url_for("start"))


@app.route("/cp", methods=["GET"])
@login_required
def control_panel():
    settings_timezone_form = SettingsSelectTimezoneForm()
    selected_timezone = Settings.query.filter_by(
        key="timezone").first().value or "America/New_York"
    # Set the currently selected timezone as default
    settings_timezone_form.timezone.choices = get_supported_timezones()
    settings_timezone_form.timezone.default = selected_timezone
    settings_timezone_form.process()
    return render_template("cp.html", settings_timezone_form=settings_timezone_form)


@app.route("/finished/<int:itemid>", methods=["GET"])
@login_required
def mark_as_finished(itemid):
    finish_item = current_user.reminders.filter_by(
        id=itemid, finished=False).first()
    if finish_item is None:
        flash("Could not find item with ID %d" % itemid, "error")
    else:
        finish_item.finished = True
        finish_item.finish_date = datetime.utcnow()
        db.session.commit()
        flash("Congratulations, you finished another task!", "success")
        return redirect(url_for("start"))
    return redirect(url_for("start"))


@app.route("/history", methods=["GET"])
@login_required
def item_history():
    all_items = Reminder.query.filter_by(user_id=current_user.id, finished=True).order_by(
        Reminder.finish_date.desc()).all()
    return render_template("history.html", reminders=all_items)


@app.route("/settings/tz", methods=["POST"])
@login_required
def cp_change_timezone():
    # Check if the selected timezone is a recognized timezone
    form = SettingsSelectTimezoneForm()
    selected_timezone = form.timezone.data
    if selected_timezone not in common_timezones:
        flash("Invalid timezone selected", "error")
        return redirect(url_for("control_panel"))
    current_timezone = Settings.query.filter_by(key="timezone").first()
    current_timezone.value = selected_timezone
    db.session.add(current_timezone)
    db.session.commit()
    flash("Timezone changed to %s" % selected_timezone, "success")
    return redirect(url_for("control_panel"))


@app.route("/edit/<itemid>", methods=["GET", "POST"])
@login_required
def edit_item(itemid):
    edit_form = EditReminderForm()
    if request.method == "POST":
        old_item = Reminder.query.filter_by(id=itemid).first()
        if old_item is None:
            flash("Could not edit because no item with this ID could be found", "error")
            return redirect(url_for("start"))
        if old_item.title != edit_form.title.data:
            flash("Titles can not be edited after the item was created", "error")
            return redirect(url_for("start"))
        # Check if selected category is valid
        try:
            category_id = int(edit_form.category.data)
        except ValueError:
            flash("Invalid category selected (NaN).", "error")
            return redirect(url_for("start"))
        selected_category = ReminderCategory.query.filter_by(
            id=category_id).first()
        if selected_category is None:
            flash("Invalid category selected (not found).", "error")
            return redirect(url_for("start"))
        old_item.description = edit_form.description.data
        old_item.category_id = category_id
        db.session.commit()
        flash("Item successfully updated.", "success")
        return redirect(url_for("start"))
    else:
        found_item = Reminder.query.filter_by(id=itemid).first()
        if found_item is None:
            flash("Invalid Item ID.", "error")
            return redirect(url_for("start"))
        else:
            edit_form.category.choices = get_categories()
            edit_form.category.default = str(ReminderCategory.query.filter_by(
                name=found_item.category.name).first().id)
            edit_form.title.default = found_item.title
            edit_form.description.default = found_item.description
            edit_form.process()
            return render_template("edit_item.html", item=found_item, edit_form=edit_form)
    return redirect(url_for("start"))


@app.route("/cp/export/items", methods=["GET", "POST"])
@login_required
def export_items():
    export_dict = {}
    app_version = AppInfo.query.filter_by(key="app_version").first()
    test = AppInfo.query.filter_by(key="app_version").first()
    all_items = Reminder.query.all()
    export_dict["app_version"] = app_version.value or "0.0"
    export_dict["items"] = all_items
    app.logger.debug("Item export finished")

    conn = sqlite3.connect('data.db')
    sql_dump = ""
    for line in conn.iterdump():
        sql_dump += '%s\n' % line
    return Response(sql_dump,
                    mimetype="application/sql",
                    headers={
                        "Content-disposition":
                            "attachment; filename=dump.sql"
                    })
