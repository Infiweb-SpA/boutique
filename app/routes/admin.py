from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Producto, Categoria, Usuario, ConfiguracionSistema
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

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

@admin_bp.app_template_filter('update_page')
def update_page_filter(args, new_page):
    """Filtro para actualizar el parámetro page en los argumentos de la URL"""
    args_dict = dict(args)
    args_dict['page'] = new_page
    return args_dict

# ==================== DASHBOARD ====================
@admin_bp.route('/')
@admin_required
def panel():
    """Panel de administración - Dashboard"""
    # Actualizar última conexión
    current_user.ultima_conexion = datetime.utcnow()
    db.session.commit()
    
    # Estadísticas generales
    total_productos = Producto.query.count()
    total_categorias = Categoria.query.count()
    total_usuarios = Usuario.query.count()
    
    # Productos con stock bajo (menos de 5 unidades)
    productos_stock_bajo = Producto.query.filter(Producto.stock < 5).filter(Producto.stock > 0).count()
    productos_agotados = Producto.query.filter(Producto.stock == 0).count()
    
    # Productos más caros
    productos_destacados = Producto.query.order_by(Producto.precio.desc()).limit(5).all()
    
    # Productos recientes (últimos 5 agregados)
    productos_recientes = Producto.query.order_by(Producto.id.desc()).limit(5).all()
    
    # Estadísticas por categoría
    categorias_stats = db.session.query(
        Categoria.nombre,
        func.count(Producto.id).label('total_productos'),
        func.sum(Producto.stock).label('total_stock')
    ).outerjoin(Producto).group_by(Categoria.id).all()
    
    return render_template('dashboard.html',
                         total_productos=total_productos,
                         total_categorias=total_categorias,
                         total_usuarios=total_usuarios,
                         productos_stock_bajo=productos_stock_bajo,
                         productos_agotados=productos_agotados,
                         productos_destacados=productos_destacados,
                         productos_recientes=productos_recientes,
                         categorias_stats=categorias_stats)

# ==================== INVENTARIO ====================
@admin_bp.route('/inventario')
@admin_required
def inventario():
    """Panel de inventario"""
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    # Filtros
    categoria_id = request.args.get('categoria_id', type=int)
    stock_filter = request.args.get('stock', 'all')
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    
    # Construir query base
    query = Producto.query
    
    # Aplicar filtros
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)
    
    if stock_filter == 'in_stock':
        query = query.filter(Producto.stock > 0)
    elif stock_filter == 'out_of_stock':
        query = query.filter(Producto.stock == 0)
    
    if precio_min is not None:
        query = query.filter(Producto.precio >= precio_min)
    
    if precio_max is not None:
        query = query.filter(Producto.precio <= precio_max)
    
    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    productos = pagination.items
    categorias = Categoria.query.all()
    
    return render_template('admininventario.html',
                         productos=productos,
                         categorias=categorias,
                         pagination=pagination,
                         filters={
                             'categoria_id': categoria_id,
                             'stock': stock_filter,
                             'precio_min': precio_min,
                             'precio_max': precio_max
                         })

# ==================== CLIENTES ====================
@admin_bp.route('/clientes')
@admin_required
def clientes():
    """Panel de clientes"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtros
    search = request.args.get('search', '')
    admin_filter = request.args.get('admin', 'all')
    
    # Construir query
    query = Usuario.query
    
    if search:
        query = query.filter(
            or_(
                Usuario.nombre.ilike(f'%{search}%'),
                Usuario.email.ilike(f'%{search}%')
            )
        )
    
    if admin_filter == 'admin':
        query = query.filter(Usuario.es_admin == True)
    elif admin_filter == 'cliente':
        query = query.filter(Usuario.es_admin == False)
    
    # Estadísticas
    total_clientes = Usuario.query.filter(Usuario.es_admin == False).count()
    total_admins = Usuario.query.filter(Usuario.es_admin == True).count()
    
    # Paginación
    pagination = query.order_by(Usuario.nombre).paginate(page=page, per_page=per_page, error_out=False)
    usuarios = pagination.items
    
    return render_template('clientes.html',
                         usuarios=usuarios,
                         pagination=pagination,
                         total_clientes=total_clientes,
                         total_admins=total_admins,
                         filters={
                             'search': search,
                             'admin': admin_filter
                         })

# ==================== PERFIL DE ADMIN ====================
@admin_bp.route('/perfil')
@admin_required
def perfil():
    """Perfil del administrador"""
    return render_template('admin_perfil.html')

@admin_bp.route('/perfil/actualizar', methods=['POST'])
@admin_required
def actualizar_perfil():
    """Actualizar perfil del administrador"""
    try:
        data = request.form
        
        # Actualizar información básica
        current_user.nombre = data['nombre']
        current_user.email = data['email']
        current_user.telefono = data.get('telefono', '')
        current_user.direccion = data.get('direccion', '')
        current_user.bio = data.get('bio', '')
        
        # Procesar avatar si se subió
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = secure_filename(f"avatar_{current_user.id}_{file.filename}")
                filepath = os.path.join('app/static/uploads/avatars', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                current_user.avatar_url = f'/static/uploads/avatars/{filename}'
        
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar perfil: {str(e)}', 'error')
    
    return redirect(url_for('admin.perfil'))

@admin_bp.route('/perfil/cambiar-password', methods=['POST'])
@admin_required
def cambiar_password():
    """Cambiar contraseña del administrador"""
    try:
        data = request.form
        password_actual = data['password_actual']
        nueva_password = data['nueva_password']
        confirmar_password = data['confirmar_password']
        
        # Verificar contraseña actual
        if not check_password_hash(current_user.password, password_actual):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('admin.perfil'))
        
        # Verificar que las nuevas contraseñas coincidan
        if nueva_password != confirmar_password:
            flash('Las nuevas contraseñas no coinciden', 'error')
            return redirect(url_for('admin.perfil'))
        
        # Verificar longitud mínima
        if len(nueva_password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('admin.perfil'))
        
        # Actualizar contraseña
        current_user.password = generate_password_hash(nueva_password)
        db.session.commit()
        
        flash('Contraseña actualizada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar contraseña: {str(e)}', 'error')
    
    return redirect(url_for('admin.perfil'))

@admin_bp.route('/perfil/preferencias', methods=['POST'])
@admin_required
def actualizar_preferencias():
    """Actualizar preferencias del usuario"""
    try:
        data = request.form
        
        current_user.notificaciones_stock = 'notificaciones_stock' in data
        current_user.notificaciones_pedidos = 'notificaciones_pedidos' in data
        current_user.tema_preferido = data.get('tema', 'light')
        current_user.idioma = data.get('idioma', 'es')
        
        db.session.commit()
        flash('Preferencias actualizadas exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar preferencias: {str(e)}', 'error')
    
    return redirect(url_for('admin.perfil'))

# ==================== CONFIGURACIÓN DEL SISTEMA ====================
@admin_bp.route('/configuracion')
@admin_required
def configuracion():
    """Panel de configuración del sistema"""
    # Obtener configuraciones actuales
    configs = {}
    for config in ConfiguracionSistema.query.all():
        configs[config.clave] = config.valor
    
    return render_template('configuracion.html', configs=configs)

@admin_bp.route('/configuracion/tienda', methods=['POST'])
@admin_required
def configuracion_tienda():
    """Guardar configuración de la tienda"""
    try:
        data = request.form
        
        # Guardar cada configuración
        configuraciones = {
            'tienda_nombre': data.get('tienda_nombre', 'ATELIER'),
            'tienda_email': data.get('tienda_email', ''),
            'tienda_telefono': data.get('tienda_telefono', ''),
            'tienda_direccion': data.get('tienda_direccion', ''),
            'tienda_descripcion': data.get('tienda_descripcion', '')
        }
        
        for clave, valor in configuraciones.items():
            config = ConfiguracionSistema.query.filter_by(clave=clave).first()
            if config:
                config.valor = valor
            else:
                config = ConfiguracionSistema(clave=clave, valor=valor)
                db.session.add(config)
        
        db.session.commit()
        flash('Configuración de la tienda guardada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar configuración: {str(e)}', 'error')
    
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/inventario', methods=['POST'])
@admin_required
def configuracion_inventario():
    """Guardar configuración de inventario"""
    try:
        data = request.form
        
        configuraciones = {
            'stock_alerta': data.get('stock_alerta', '5'),
            'productos_por_pagina': data.get('productos_por_pagina', '12'),
            'moneda': data.get('moneda', 'CLP'),
            'simbolo_moneda': data.get('simbolo_moneda', '$')
        }
        
        for clave, valor in configuraciones.items():
            config = ConfiguracionSistema.query.filter_by(clave=clave).first()
            if config:
                config.valor = valor
            else:
                config = ConfiguracionSistema(clave=clave, valor=valor)
                db.session.add(config)
        
        db.session.commit()
        flash('Configuración de inventario guardada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar configuración: {str(e)}', 'error')
    
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/apariencia', methods=['POST'])
@admin_required
def configuracion_apariencia():
    """Guardar configuración de apariencia"""
    try:
        data = request.form
        
        configuraciones = {
            'tema_default': data.get('tema_default', 'light'),
            'tipografia_titulos': data.get('tipografia_titulos', 'Noto Serif'),
            'color_acento': data.get('color_acento', '#745b3b')
        }
        
        for clave, valor in configuraciones.items():
            config = ConfiguracionSistema.query.filter_by(clave=clave).first()
            if config:
                config.valor = valor
            else:
                config = ConfiguracionSistema(clave=clave, valor=valor)
                db.session.add(config)
        
        db.session.commit()
        flash('Configuración de apariencia guardada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar configuración: {str(e)}', 'error')
    
    return redirect(url_for('admin.configuracion'))

# ==================== GESTIÓN DE PRODUCTOS ====================
@admin_bp.route('/producto/crear', methods=['POST'])
@admin_required
def crear_producto():
    """Crear nuevo producto"""
    try:
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
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear el producto: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventario'))

@admin_bp.route('/producto/editar/<int:id>', methods=['POST'])
@admin_required
def editar_producto(id):
    """Editar producto existente"""
    try:
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
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el producto: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventario'))

@admin_bp.route('/producto/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_producto(id):
    """Eliminar producto"""
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventario'))

@admin_bp.route('/producto/<int:id>')
@admin_required
def obtener_producto(id):
    """Obtener datos de un producto para edición"""
    try:
        producto = Producto.query.get_or_404(id)
        return jsonify({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'stock': producto.stock,
            'imagen_url': producto.imagen_url,
            'sku': producto.sku,
            'categoria_id': producto.categoria_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# ==================== GESTIÓN DE CATEGORÍAS ====================
@admin_bp.route('/categoria/crear', methods=['POST'])
@admin_required
def crear_categoria():
    """Crear nueva categoría"""
    try:
        data = request.form
        categoria = Categoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', '')
        )
        db.session.add(categoria)
        db.session.commit()
        flash('Categoría creada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la categoría: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventario'))

@admin_bp.route('/categoria/editar/<int:id>', methods=['POST'])
@admin_required
def editar_categoria(id):
    """Editar categoría existente"""
    try:
        categoria = Categoria.query.get_or_404(id)
        data = request.form
        
        categoria.nombre = data['nombre']
        categoria.descripcion = data.get('descripcion', '')
        
        db.session.commit()
        flash('Categoría actualizada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la categoría: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventario'))

@admin_bp.route('/categoria/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_categoria(id):
    """Eliminar categoría"""
    try:
        categoria = Categoria.query.get_or_404(id)
        
        # Verificar si hay productos asociados
        if categoria.productos:
            flash('No se puede eliminar la categoría porque tiene productos asociados', 'error')
            return redirect(url_for('admin.inventario'))
        
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la categoría: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventario'))

# ==================== GESTIÓN DE USUARIOS ====================
@admin_bp.route('/usuario/toggle-admin/<int:id>', methods=['POST'])
@admin_required
def toggle_admin(id):
    """Cambiar estado de administrador de un usuario"""
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # No permitir que un admin se quite a sí mismo los permisos
        if usuario.id == current_user.id:
            flash('No puedes modificar tus propios permisos de administrador', 'error')
            return redirect(url_for('admin.clientes'))
        
        usuario.es_admin = not usuario.es_admin
        db.session.commit()
        
        estado = "administrador" if usuario.es_admin else "cliente"
        flash(f'Usuario {usuario.nombre} ahora es {estado}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar permisos: {str(e)}', 'error')
    
    return redirect(url_for('admin.clientes'))

# ==================== API ====================
@admin_bp.route('/api/estadisticas')
@admin_required
def api_estadisticas():
    """API para obtener estadísticas en tiempo real"""
    try:
        stats = {
            'total_productos': Producto.query.count(),
            'total_categorias': Categoria.query.count(),
            'total_usuarios': Usuario.query.count(),
            'productos_stock_bajo': Producto.query.filter(Producto.stock < 5).filter(Producto.stock > 0).count(),
            'productos_agotados': Producto.query.filter(Producto.stock == 0).count(),
            'total_clientes': Usuario.query.filter(Usuario.es_admin == False).count(),
            'total_admins': Usuario.query.filter(Usuario.es_admin == True).count()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MANEJADORES DE ERROR ====================
@admin_bp.errorhandler(404)
def not_found_error(error):
    """Manejador de error 404 para rutas de admin"""
    flash('El recurso solicitado no existe', 'error')
    return redirect(url_for('admin.panel'))

@admin_bp.errorhandler(500)
def internal_error(error):
    """Manejador de error 500 para rutas de admin"""
    db.session.rollback()
    flash('Ocurrió un error interno. Por favor, intenta nuevamente', 'error')
    return redirect(url_for('admin.panel'))