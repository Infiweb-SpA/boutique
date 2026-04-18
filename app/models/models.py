from flask_login import UserMixin
from datetime import datetime
from app import db

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Nuevos campos para el perfil
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    ultima_conexion = db.Column(db.DateTime)
    
    # Configuración de usuario
    notificaciones_stock = db.Column(db.Boolean, default=True)
    notificaciones_pedidos = db.Column(db.Boolean, default=True)
    tema_preferido = db.Column(db.String(20), default='light')
    idioma = db.Column(db.String(10), default='es')
    
    def set_password(self, password):
        """Establecer contraseña hasheada"""
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    
    productos = db.relationship('Producto', back_populates='categoria')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen_url = db.Column(db.String(500))
    sku = db.Column(db.String(50), unique=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    categoria = db.relationship('Categoria', back_populates='productos')
    carrito_items = db.relationship('CarritoItem', back_populates='producto')
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'

class CarritoItem(db.Model):
    __tablename__ = 'carrito_items'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer, default=1)
    talla = db.Column(db.String(10), default='M')
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)
    
    producto = db.relationship('Producto', back_populates='carrito_items')
    
    def __repr__(self):
        return f'<CarritoItem {self.producto.nombre if self.producto else "N/A"} x{self.cantidad}>'

class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='text')  # text, number, boolean, json
    
    def __repr__(self):
        return f'<Configuracion {self.clave}>'