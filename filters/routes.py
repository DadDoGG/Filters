from flask import render_template, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from .forms import LoginForm, RegisterForm
from filters import app, db
from .models import User



@app.get('/')
def index():
    return render_template('index.html', current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            rm = form.remember.data
            login_user(user, remember=rm)
            return redirect('/')
        else:
            return ("Неверная пара логин/пароль", "error")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    print("Вы успешно вышли из аккаунта", "success")
    return redirect('/login')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(form.password.data)
            res = User(email=form.email.data, login=form.login.data,
                       permission = 'user', password=hash, is_active = False)
            db.session.add(res)
            db.session.commit()
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", form=form)


