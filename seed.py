#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba.
Este script también crea la base de datos, las tablas y el usuario administrador.

Ejecutar con: python seed.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Categoria, Producto, CarritoItem, Usuario

IMAGENES_POR_CATEGORIA = {
    'Pantalones': [
        'https://images.pexels.com/photos/1598507/pexels-photo-1598507.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/4210866/pexels-photo-4210866.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/6567607/pexels-photo-6567607.jpeg?auto=compress&cs=tinysrgb&w=600',
    ],
    'Poleras': [
        'https://images.pexels.com/photos/428340/pexels-photo-428340.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/6311390/pexels-photo-6311390.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/845434/pexels-photo-845434.jpeg?auto=compress&cs=tinysrgb&w=600',
    ],
    'Chombas': [
        'https://images.pexels.com/photos/28990954/pexels-photo-28990954.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/28975312/pexels-photo-28975312.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/934070/pexels-photo-934070.jpeg?auto=compress&cs=tinysrgb&w=600',
    ],
    'Chaquetas': [
        'https://images.pexels.com/photos/2908880/pexels-photo-2908880.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/28990954/pexels-photo-28990954.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/1462637/pexels-photo-1462637.jpeg?auto=compress&cs=tinysrgb&w=600',
    ],
    'Accesorios': [
        'https://images.pexels.com/photos/1152077/pexels-photo-1152077.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/1445696/pexels-photo-1445696.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/264614/pexels-photo-264614.jpeg?auto=compress&cs=tinysrgb&w=600',
    ]
}

def create_database_directory():
    """Crear el directorio de la base de datos si no existe"""
    db_dir = os.path.join(os.path.dirname(__file__), 'app', 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"  📁 Directorio creado: {db_dir}")

def init_database():
    """Inicializar la base de datos (crear tablas)"""
    print("  🏗️  Creando tablas en la base de datos...")
    db.create_all()
    print("     ✓ Tablas creadas exitosamente")

def create_admin_user():
    """Crear usuario administrador"""
    print("\n  👤 Creando usuario administrador...")
    
    # Verificar si ya existe
    existing = Usuario.query.filter_by(email='admin@boutique.com').first()
    if existing:
        print("     ℹ️  El usuario admin ya existe")
        return existing
    
    admin = Usuario(
        email='admin@boutique.com',
        nombre='Administrador',
        es_admin=True
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    print("     ✓ Usuario administrador creado:")
    print("        📧 Email: admin@boutique.com")
    print("        🔑 Password: admin123")
    
    return admin

def seed_database():
    """Poblar la base de datos con datos iniciales"""
    
    print("\n" + "="*60)
    print("🌱 ATELIER BOUTIQUE - Inicializando Base de Datos")
    print("="*60 + "\n")
    
    # 1. Crear directorio para la base de datos
    create_database_directory()
    
    # 2. Crear tablas
    init_database()
    
    # 3. Crear usuario administrador
    create_admin_user()
    
    # 4. Limpiar datos existentes (excepto usuarios)
    print("\n  🧹 Limpiando datos de productos...")
    try:
        CarritoItem.query.delete()
        Producto.query.delete()
        Categoria.query.delete()
        db.session.commit()
        print("     ✓ Datos anteriores eliminados")
    except:
        print("     ℹ️  No había datos previos para eliminar")
    
    # 5. Crear categorías
    print("\n  📁 Creando categorías...")
    categorias_data = [
        {'nombre': 'Pantalones', 'descripcion': 'Pantalones de diseño exclusivo con cortes precisos'},
        {'nombre': 'Poleras', 'descripcion': 'Poleras de algodón premium y cortes minimalistas'},
        {'nombre': 'Chombas', 'descripcion': 'Chombas y sweaters de lana merino y cashmere'},
        {'nombre': 'Chaquetas', 'descripcion': 'Chaquetas estructuradas, blazers y abrigos'},
        {'nombre': 'Accesorios', 'descripcion': 'Accesorios de lujo para completar tu look'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria = Categoria(**cat_data)
        db.session.add(categoria)
        categorias[cat_data['nombre']] = categoria
    
    db.session.commit()
    print(f"     ✓ {len(categorias)} categorías creadas")
    
    # 6. Crear productos
    print("\n  👕 Creando productos...")
    productos_data = [
        {'nombre': 'Pantalón Sastre Lino', 'categoria': 'Pantalones', 'precio': 185000, 'stock': 15, 'sku': 'PT-001'},
        {'nombre': 'Pantalón Wide Leg', 'categoria': 'Pantalones', 'precio': 145000, 'stock': 20, 'sku': 'PT-002'},
        {'nombre': 'Jeans Selvedge', 'categoria': 'Pantalones', 'precio': 165000, 'stock': 12, 'sku': 'PT-003'},
        {'nombre': 'Pantalón de Vestir Lana Fría', 'categoria': 'Pantalones', 'precio': 195000, 'stock': 8, 'sku': 'PT-004'},
        {'nombre': 'Polera Algodón Pima', 'categoria': 'Poleras', 'precio': 45000, 'stock': 50, 'sku': 'PO-001'},
        {'nombre': 'Polera Oversized Premium', 'categoria': 'Poleras', 'precio': 42000, 'stock': 45, 'sku': 'PO-002'},
        {'nombre': 'Polera Cuello Redondo', 'categoria': 'Poleras', 'precio': 38000, 'stock': 60, 'sku': 'PO-003'},
        {'nombre': 'Polera Manga Larga', 'categoria': 'Poleras', 'precio': 52000, 'stock': 35, 'sku': 'PO-004'},
        {'nombre': 'Chomba Merino Texturada', 'categoria': 'Chombas', 'precio': 120000, 'stock': 18, 'sku': 'CH-001'},
        {'nombre': 'Chomba Cashmere Pura', 'categoria': 'Chombas', 'precio': 250000, 'stock': 5, 'sku': 'CH-002'},
        {'nombre': 'Cárdigan Lana Gruesa', 'categoria': 'Chombas', 'precio': 135000, 'stock': 12, 'sku': 'CH-003'},
        {'nombre': 'Blazer Estructurado', 'categoria': 'Chaquetas', 'precio': 220000, 'stock': 8, 'sku': 'CQ-001'},
        {'nombre': 'Chaqueta de Cuero', 'categoria': 'Chaquetas', 'precio': 350000, 'stock': 4, 'sku': 'CQ-002'},
        {'nombre': 'Abrigo de Lana', 'categoria': 'Chaquetas', 'precio': 280000, 'stock': 6, 'sku': 'CQ-003'},
        {'nombre': 'Bolso Tote de Cuero', 'categoria': 'Accesorios', 'precio': 180000, 'stock': 7, 'sku': 'AC-001'},
        {'nombre': 'Cinturón Artesanal', 'categoria': 'Accesorios', 'precio': 65000, 'stock': 20, 'sku': 'AC-002'},
        {'nombre': 'Bufanda de Seda', 'categoria': 'Accesorios', 'precio': 85000, 'stock': 15, 'sku': 'AC-003'},
    ]
    
    producto_count = 0
    for idx, prod_data in enumerate(productos_data):
        categoria = categorias[prod_data['categoria']]
        imagenes_cat = IMAGENES_POR_CATEGORIA.get(prod_data['categoria'], IMAGENES_POR_CATEGORIA['Poleras'])
        imagen_url = imagenes_cat[idx % len(imagenes_cat)]
        
        producto = Producto(
            nombre=prod_data['nombre'],
            descripcion=f"{prod_data['nombre']} de nuestra colección permanente. Confeccionado con materiales de la más alta calidad y un diseño atemporal que perdura.",
            precio=prod_data['precio'],
            stock=prod_data['stock'],
            sku=prod_data['sku'],
            imagen_url=imagen_url,
            categoria_id=categoria.id
        )
        db.session.add(producto)
        producto_count += 1
    
    db.session.commit()
    print(f"     ✓ {producto_count} productos creados")
    
    # 7. Crear items de carrito demo
    print("\n  🛒 Creando items de carrito de ejemplo...")
    productos = Producto.query.limit(3).all()
    items_creados = 0
    for producto in productos:
        if producto.stock > 0:
            item = CarritoItem(
                session_id='demo-session-123',
                producto_id=producto.id,
                cantidad=1,
                talla='M'
            )
            db.session.add(item)
            items_creados += 1
    
    db.session.commit()
    print(f"     ✓ {items_creados} items de carrito demo creados")
    
    # Resumen final
    print("\n" + "="*60)
    print("✅ ¡Base de datos inicializada exitosamente!")
    print("="*60)
    print("\n📊 Resumen de la Base de Datos:")
    print(f"   ├── Usuarios: {Usuario.query.count()}")
    print(f"   ├── Categorías: {Categoria.query.count()}")
    print(f"   ├── Productos: {Producto.query.count()}")
    print(f"   └── Items en carrito demo: {CarritoItem.query.count()}")
    
    total_stock = db.session.query(db.func.sum(Producto.stock)).scalar() or 0
    valor_inventario = db.session.query(db.func.sum(Producto.precio * Producto.stock)).scalar() or 0
    
    print(f"\n💰 Valor total del inventario: ${valor_inventario:,.0f}".replace(',', '.'))
    print(f"📦 Unidades totales en stock: {total_stock}")
    
    print("\n🔐 Credenciales de Administrador:")
    print("   📧 Email: admin@boutique.com")
    print("   🔑 Password: admin123")
    print("   🔗 Login: http://localhost:5000/login")
    
    print("\n🚀 ¡Listo! Ahora puedes ejecutar: python run.py\n")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()