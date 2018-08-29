from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, RecordForm, ProfileForm
from app.models import User, Record
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    return redirect(url_for('records'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user, title=user.username)

@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users, title='Community')

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, title='Edit Profile')

@app.route('/records')
@login_required
def records():
    records = Record.query.filter_by(user_id=current_user.id)
    return render_template('records.html', records=records)

@app.route('/record/<id>')
@login_required
def view_record(id):
    record = Record.query.filter_by(id=id).first_or_404()
    return render_template('view_record.html', record=record, title=record.album)

@app.route('/record/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(id):
    record = Record.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = RecordForm()
    if form.validate_on_submit():
        record.artist = form.artist.data
        record.album = form.album.data
        record.year_released = form.year_released.data
        record.year_printed = form.year_printed.data
        record.condition = form.condition.data
        db.session.commit()
        flash('Your record has been updated.')
        return redirect(url_for('records'))
    elif request.method == 'GET':
        form.artist.data = record.artist
        form.album.data = record.album
        form.year_released.data = record.year_released
        form.year_printed.data = record.year_printed
        form.condition.data = record.condition
    return render_template('edit_record.html', form=form, id=id, title='Edit Record')

@app.route('/record/create', methods=['GET', 'POST'])
@login_required
def create_record():
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(
            artist=form.artist.data,
            album=form.album.data,
            year_released=form.year_released.data,
            year_printed=form.year_printed.data,
            condition=form.condition.data,
            user_id=current_user.id
        )
        db.session.add(record)
        db.session.commit()
        flash('Record created!')
        return redirect(url_for('records'))
    return render_template('create_record.html', form=form, title='Create')

