from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Giriş başarılı.', 'success')
            if user.role == 'admin':
                return redirect(url_for('tickets.dashboard'))
            else:
                return redirect(url_for('tickets.create_ticket'))
        else:
            flash('Kullanıcı adı veya şifre hatalı.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Oturum kapatıldı.', 'info')
    return redirect(url_for('auth.login'))
