from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(100))
    es_admin = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')
    
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
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    @property
    def disponible(self):
        return self.stock > 0

class CarritoItem(db.Model):
    __tablename__ = 'carrito_items'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer, default=1)
    talla = db.Column(db.String(10), default='M')
    color = db.Column(db.String(50), default='Antracita')  # NUEVO CAMPO
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)
    
    producto = db.relationship('Producto', backref='carrito_items')
    
    def __repr__(self):
        return f'<CarritoItem {self.producto.nombre} x {self.cantidad}>'
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad