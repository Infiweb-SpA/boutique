from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Producto, Categoria, CarritoItem, Usuario
import uuid
from functools import wraps

main_bp = Blueprint('main', __name__)

def get_session_id():
    """Obtiene o crea un session_id para el carrito"""
    if 'cart_session_id' not in session:
        session['cart_session_id'] = str(uuid.uuid4())
    return session['cart_session_id']

def admin_required(f):
    """Decorador para rutas que requieren ser administrador"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.es_admin:
            flash('No tienes permisos para acceder a esta sección.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# ============ RUTAS PÚBLICAS ============

@main_bp.route('/')
def index():
    """Página principal - Catálogo Desktop"""
    categoria_id = request.args.get('categoria', type=int)
    categorias = Categoria.query.all()
    
    query = Producto.query
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    productos = query.all()
    categoria_activa = categoria_id
    
    return render_template('index.html', 
                         productos=productos, 
                         categorias=categorias,
                         categoria_activa=categoria_activa)

@main_bp.route('/movil')
def index_movil():
    """Versión móvil del catálogo"""
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    return render_template('catalogomovil.html', 
                         productos=productos, 
                         categorias=categorias)

@main_bp.route('/producto/<int:id>')
def producto(id):
    """Página de detalle de producto"""
    producto = Producto.query.get_or_404(id)
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    if is_mobile:
        return render_template('detallesmovil.html', producto=producto)
    return render_template('detallesdesktop.html', producto=producto)

@main_bp.route('/carrito')
def carrito():
    """Página del carrito de compras"""
    session_id = get_session_id()
    items = CarritoItem.query.filter_by(session_id=session_id).all()
    
    subtotal = sum(item.subtotal for item in items)
    total = subtotal
    
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    template = 'carritomovil.html' if is_mobile else 'carritodeskop.html'
    return render_template(template, items=items, subtotal=subtotal, total=total)

# ============ API CARRITO ============

@main_bp.route('/api/carrito/agregar', methods=['POST'])
def api_agregar_carrito():
    """API para agregar items al carrito"""
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)
    talla = data.get('talla', 'M')
    color = data.get('color', 'Antracita')  # NUEVO: recibir color
    
    producto = Producto.query.get_or_404(producto_id)
    
    if producto.stock < cantidad:
        return jsonify({'error': 'Stock insuficiente'}), 400
    
    session_id = get_session_id()
    
    # Buscar si ya existe el item con misma talla Y color
    item = CarritoItem.query.filter_by(
        session_id=session_id,
        producto_id=producto_id,
        talla=talla,
        color=color  # NUEVO: filtrar por color
    ).first()
    
    if item:
        item.cantidad += cantidad
    else:
        item = CarritoItem(
            session_id=session_id,
            producto_id=producto_id,
            cantidad=cantidad,
            talla=talla,
            color=color  # NUEVO: guardar color
        )
        db.session.add(item)
    
    db.session.commit()
    
    total_items = CarritoItem.query.filter_by(session_id=session_id).count()
    
    return jsonify({
        'success': True,
        'message': 'Producto agregado al carrito',
        'total_items': total_items
    })

@main_bp.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
def api_actualizar_carrito(item_id):
    """API para actualizar cantidad de un item"""
    data = request.get_json()
    cantidad = data.get('cantidad')
    
    item = CarritoItem.query.get_or_404(item_id)
    
    if cantidad <= 0:
        db.session.delete(item)
    else:
        if item.producto.stock < cantidad:
            return jsonify({'error': 'Stock insuficiente'}), 400
        item.cantidad = cantidad
    
    db.session.commit()
    
    return jsonify({'success': True})

@main_bp.route('/api/carrito/eliminar/<int:item_id>', methods=['DELETE'])
def api_eliminar_carrito(item_id):
    """API para eliminar un item del carrito"""
    item = CarritoItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True})

# ============ AUTENTICACIÓN ============

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login para administradores"""
    if current_user.is_authenticated:
        return redirect(url_for('main.admin'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password) and usuario.es_admin:
            login_user(usuario, remember=remember)
            flash('¡Bienvenido al panel de administración!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.admin'))
        else:
            flash('Email o contraseña incorrectos, o no tienes permisos de administrador.', 'error')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('main.index'))

# ============ RUTAS DE ADMINISTRACIÓN (PROTEGIDAS) ============

@main_bp.route('/admin')
@admin_required
def admin():
    """Panel de administración"""
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template('admininventario.html', 
                         productos=productos, 
                         categorias=categorias)

@main_bp.route('/admin/producto/crear', methods=['POST'])
@admin_required
def admin_crear_producto():
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
    return redirect(url_for('main.admin'))

@main_bp.route('/admin/producto/editar/<int:id>', methods=['POST'])
@admin_required
def admin_editar_producto(id):
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
    return redirect(url_for('main.admin'))

@main_bp.route('/admin/producto/eliminar/<int:id>', methods=['POST'])
@admin_required
def admin_eliminar_producto(id):
    """Eliminar producto"""
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('main.admin'))

@main_bp.route('/catalogo-movil')
def catalogomovil():
    """Versión móvil del catálogo"""
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    return render_template('catalogomovil.html', 
                         productos=productos, 
                         categorias=categorias)

