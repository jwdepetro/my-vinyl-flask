from datetime import datetime

import requests
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, RecordForm, ProfileForm, MessageForm
from app.models import User, Record, Message


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    records = Record.query.filter_by(user_id=current_user.id)
    return render_template('my-vinyl.html', records=records)


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
    records = Record.query.all()
    return render_template('records.html', records=records)


@app.route('/record/<id>')
@login_required
def view_record(id):
    record = Record.query.filter_by(id=id).first_or_404()
    data = {}
    if record.mbid:
        r = requests.get(
            'http://ws.audioscrobbler.com/2.0/'
            '?method=album.getinfo'
            '&mbid=' + record.mbid +
            '&api_key=' + app.config['LAST_API_KEY'] +
            '&format=json'
        )
        data = r.json()
    return render_template('view_record.html', record=record, data=data, title=record.album)


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
    mbid = request.args.get('mbid')
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(
            artist=form.artist.data,
            album=form.album.data,
            year_released=form.year_released.data,
            year_printed=form.year_printed.data,
            condition=form.condition.data,
            user_id=current_user.id,
            mbid=mbid
        )
        db.session.add(record)
        db.session.commit()
        flash('Record created!')
        return redirect(url_for('records'))
    if mbid is not None:
        r = requests.get(
            'http://ws.audioscrobbler.com/2.0/'
            '?method=album.getinfo'
            '&mbid=' + mbid +
            '&api_key=' + app.config['LAST_API_KEY'] +
            '&format=json'
        )
        data = r.json()
        form.album.data = data['album']['name']
        form.artist.data = data['album']['artist']

    return render_template('create_record.html', form=form, mbid=mbid, title='Create')


@app.route('/search', methods=['GET'])
@login_required
def search():
    data = {}
    q = request.args.get('q')
    if q :
        r = requests.get(
            'http://ws.audioscrobbler.com/2.0/'
            '?method=album.search'
            '&album=' + q +
            '&api_key=' + app.config['LAST_API_KEY'] +
            '&format=json'
        )
        data = r.json()
    else:
        q = ''
    return render_template('search.html', data=data, q=q)


@app.route('/search/detail/<mbid>', methods=['GET'])
@login_required
def search_detail(mbid):
    r = requests.get(
        'http://ws.audioscrobbler.com/2.0/'
        '?method=album.getinfo'
        '&mbid=' + mbid +
        '&api_key=' + app.config['LAST_API_KEY'] +
        '&format=json'
    )
    return render_template('search_detail.html', data=r.json())


@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            author=current_user,
            recipient=user,
            body=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('send_message', recipient=recipient))
    return render_template('send_message.html', title='Send Message', form=form, recipient=recipient)


@app.route('/messages', methods=['GET'])
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()

    outbox_page = request.args.get('outbox_page', 1, type=int)
    outbox = current_user.messages_sent.order_by(
        Message.timestamp.desc()).paginate(
        outbox_page, 10, False)
    outbox_next_url = url_for('messages', outbox_page=outbox.next_num) \
        if outbox.has_next else None
    outbox_prev_url = url_for('messages', outbox_page=outbox.prev_num) \
        if outbox.has_prev else None

    inbox_page = request.args.get('inbox_page', 1, type=int)
    inbox = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
        inbox_page, 10, False)
    inbox_next_url = url_for('messages', inbox_page=inbox.next_num) \
        if inbox.has_next else None
    inbox_prev_url = url_for('messages', inbox_page=inbox.prev_num) \
        if inbox.has_prev else None

    return render_template('messages.html', inbox=inbox.items, outbox=outbox.items,
                           inbox_next_url=inbox_next_url, inbox_prev_url=inbox_prev_url,
                           outbox_next_url=outbox_next_url, outbox_prev_url=outbox_prev_url)


