from app import app, db
from flask import render_template, redirect, url_for, request
from app.forms import LoginForm, SignupForm
from catalyst.models import User
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.routing import BuildError


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=form.email.data.lower()).first()

        # login fails if user not found or password incorrect
        if user is None or not user.check_password(form.password.data):
            return render_template('auth/login.html', **locals(), login_failed=True)

        login_user(user, remember=False)  # default remember users, set to False to check if connection issue persists

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = 'index'

        # print(next_page)
        # print(url_for(next_page))
        try:
            return redirect(url_for(next_page))
        except BuildError:
            return redirect(url_for('index'))

    return render_template('auth/login.html', **locals())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))