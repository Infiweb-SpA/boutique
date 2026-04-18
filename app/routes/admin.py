from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Producto, Categoria

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador para rutas que requieren ser administrador"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.es_admin:
            flash('No tienes permisos para acceder a esta sección.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def panel():
    """Panel de administración"""
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template('admininventario.html',
                         productos=productos,
                         categorias=categorias)

@admin_bp.route('/producto/crear', methods=['POST'])
@admin_required
def crear_producto():
    """Crear nuevo producto"""
    data = request.form
    producto = Producto(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        precio=float(data['precio']),
        stock=int(data.get('stock', 0)),
        imagen_url=data.get('imagen_url', ''),
        sku=data.get('sku', ''),
        categoria_id=int(data['categoria_id']) if data.get('categoria_id') else None
    )
    db.session.add(producto)
    db.session.commit()
    flash('Producto creado exitosamente', 'success')
    return redirect(url_for('admin.panel'))

@admin_bp.route('/producto/editar/<int:id>', methods=['POST'])
@admin_required
def editar_producto(id):
    """Editar producto existente"""
    producto = Producto.query.get_or_404(id)
    data = request.form

    producto.nombre = data['nombre']
    producto.descripcion = data.get('descripcion', '')
    producto.precio = float(data['precio'])
    producto.stock = int(data.get('stock', 0))
    producto.imagen_url = data.get('imagen_url', '')
    producto.sku = data.get('sku', '')
    producto.categoria_id = int(data['categoria_id']) if data.get('categoria_id') else None

    db.session.commit()
    flash('Producto actualizado exitosamente', 'success')
    return redirect(url_for('admin.panel'))

@admin_bp.route('/producto/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_producto(id):
    """Eliminar producto"""
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('admin.panel'))