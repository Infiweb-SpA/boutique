from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login para administradores"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.panel'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password) and usuario.es_admin:
            login_user(usuario, remember=remember)
            flash('¡Bienvenido al panel de administración!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.panel'))
        else:
            flash('Email o contraseña incorrectos, o no tienes permisos de administrador.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('public.index'))