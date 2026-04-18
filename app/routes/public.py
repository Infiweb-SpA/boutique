from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from app import db
from app.models import Producto, Categoria, CarritoItem
import uuid

public_bp = Blueprint('public', __name__)

def get_session_id():
    """Obtiene o crea un session_id para el carrito"""
    if 'cart_session_id' not in session:
        session['cart_session_id'] = str(uuid.uuid4())
    return session['cart_session_id']

# ============ RUTAS PÚBLICAS ============

@public_bp.route('/')
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

@public_bp.route('/movil')
def index_movil():
    """Versión móvil del catálogo"""
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    return render_template('catalogomovil.html',
                         productos=productos,
                         categorias=categorias)

@public_bp.route('/producto/<int:id>')
def producto(id):
    """Página de detalle de producto"""
    producto = Producto.query.get_or_404(id)
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])

    if is_mobile:
        return render_template('detallesmovil.html', producto=producto)
    return render_template('detallesdesktop.html', producto=producto)

@public_bp.route('/carrito')
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

@public_bp.route('/catalogo-movil')
def catalogomovil():
    """Versión móvil del catálogo (alias)"""
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    return render_template('catalogomovil.html',
                         productos=productos,
                         categorias=categorias)

# ============ API CARRITO ============

@public_bp.route('/api/carrito/agregar', methods=['POST'])
def api_agregar_carrito():
    """API para agregar items al carrito"""
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)
    talla = data.get('talla', 'M')
    color = data.get('color', 'Antracita')

    producto = Producto.query.get_or_404(producto_id)

    if producto.stock < cantidad:
        return jsonify({'error': 'Stock insuficiente'}), 400

    session_id = get_session_id()

    item = CarritoItem.query.filter_by(
        session_id=session_id,
        producto_id=producto_id,
        talla=talla,
        color=color
    ).first()

    if item:
        item.cantidad += cantidad
    else:
        item = CarritoItem(
            session_id=session_id,
            producto_id=producto_id,
            cantidad=cantidad,
            talla=talla,
            color=color
        )
        db.session.add(item)

    db.session.commit()

    total_items = CarritoItem.query.filter_by(session_id=session_id).count()

    return jsonify({
        'success': True,
        'message': 'Producto agregado al carrito',
        'total_items': total_items
    })

@public_bp.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
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

@public_bp.route('/api/carrito/eliminar/<int:item_id>', methods=['DELETE'])
def api_eliminar_carrito(item_id):
    """API para eliminar un item del carrito"""
    item = CarritoItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    return jsonify({'success': True})