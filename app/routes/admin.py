from app import app, db
from flask import render_template, redirect, url_for, request
from app.forms import LoginForm, SignupForm
from catalyst.models import User, Task, Customer
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.routing import BuildError
from flask_user import roles_required
from flask_login import current_user, login_required


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
# @roles_required('admin')
def admin_users():
    users = User.query.all()
    form = SignupForm(request.form)

    if request.method == 'POST' and form.validate():

        user = User.objects(email=form.email.data.lower()).first()

        if user:
            user_exists = True
        else:
            user = User(email=form.email.data.lower(), firstName=form.first_name.data, lastName=form.last_name.data)
            user.set_password(form.password.data)
            user.save()

            return redirect(url_for('login'))

    return render_template('admin/users.html', nbar='admin', **locals())



@app.route('/admin/tasks', methods=['GET', 'POST'])
@login_required
# @roles_required('admin')
def admin_tasks():
    tasks = Task.query.order_by(Task.created.desc()).all()


    return render_template('admin/tasks.html', nbar='admin', **locals())


@app.route('/admin/customers', methods=['GET', 'POST'])
@login_required
# @roles_required('admin')
def admin_customers():
    customers = Customer.query.all()


    return render_template('admin/customers.html', nbar='admin', **locals())