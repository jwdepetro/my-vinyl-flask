from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, RecordForm
from app.models import User, Record
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

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

@app.route('/records')
@login_required
def records():
    records = Record.query.all()
    return render_template('records.html', records=records, title='Records')

@app.route('/record/<id>')
@login_required
def view_record(id):
    record = Record.query.filter_by(id=id).first_or_404()
    return render_template('view_record.html', record=record, title=record.album)

@app.route('/record/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(id):
    record = Record.query.filter_by(id=id).first_or_404()
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
    return render_template('edit_record.html', form=form, id=id, title='Edit')

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
            condition=form.condition.data
        )
        db.session.add(record)
        db.session.commit()
        flash('Record created!')
        return redirect(url_for('records'))
    return render_template('create_record.html', form=form, title='Create')

