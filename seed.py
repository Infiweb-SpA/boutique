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
from app.models import Categoria, Producto, CarritoItem, Usuario, ConfiguracionSistema
from datetime import datetime

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

# Avatares de ejemplo para usuarios
AVATARES_EJEMPLO = [
    'https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=200',
    'https://images.pexels.com/photos/1043471/pexels-photo-1043471.jpeg?auto=compress&cs=tinysrgb&w=200',
    'https://images.pexels.com/photos/428364/pexels-photo-428364.jpeg?auto=compress&cs=tinysrgb&w=200',
]

def create_database_directory():
    """Crear el directorio de la base de datos si no existe"""
    db_dir = os.path.join(os.path.dirname(__file__), 'app', 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"  📁 Directorio creado: {db_dir}")
    
    # Crear directorio para avatares
    avatars_dir = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads', 'avatars')
    if not os.path.exists(avatars_dir):
        os.makedirs(avatars_dir)
        print(f"  📁 Directorio de avatares creado: {avatars_dir}")

def init_database():
    """Inicializar la base de datos (crear tablas)"""
    print("  🏗️  Creando tablas en la base de datos...")
    db.create_all()
    print("     ✓ Tablas creadas exitosamente")

def create_admin_user():
    """Crear usuario administrador con campos adicionales"""
    print("\n  👤 Creando usuario administrador...")
    
    # Verificar si ya existe
    existing = Usuario.query.filter_by(email='admin@atelier.com').first()
    if existing:
        print("     ℹ️  El usuario admin ya existe")
        # Actualizar campos adicionales si no están configurados
        if not existing.telefono:
            existing.telefono = '+56 9 1234 5678'
            existing.direccion = 'Av. Providencia 1234, Santiago'
            existing.bio = 'Administrador principal de ATELIER Boutique. Experto en moda de alta costura y gestión de inventario.'
            existing.avatar_url = AVATARES_EJEMPLO[0]
            existing.notificaciones_stock = True
            existing.notificaciones_pedidos = True
            existing.tema_preferido = 'light'
            existing.idioma = 'es'
            existing.ultima_conexion = datetime.utcnow()
            db.session.commit()
            print("     ✓ Campos adicionales actualizados")
        return existing
    
    admin = Usuario(
        email='admin@atelier.com',
        nombre='Administrador',
        es_admin=True,
        telefono='+56 9 1234 5678',
        direccion='Av. Providencia 1234, Santiago',
        bio='Administrador principal de ATELIER Boutique. Experto en moda de alta costura y gestión de inventario.',
        avatar_url=AVATARES_EJEMPLO[0],
        notificaciones_stock=True,
        notificaciones_pedidos=True,
        tema_preferido='light',
        idioma='es',
        fecha_registro=datetime.utcnow(),
        ultima_conexion=datetime.utcnow()
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    print("     ✓ Usuario administrador creado:")
    print("        📧 Email: admin@atelier.com")
    print("        🔑 Password: admin123")
    print("        👤 Perfil: Completo con avatar y preferencias")
    
    return admin

def create_test_users():
    """Crear usuarios de prueba (clientes)"""
    print("\n  👥 Creando usuarios de prueba...")
    
    usuarios_test = [
        {
            'nombre': 'María González',
            'email': 'maria@ejemplo.com',
            'password': 'cliente123',
            'telefono': '+56 9 8765 4321',
            'direccion': 'Las Condes, Santiago',
            'bio': 'Cliente frecuente, amante de la moda sostenible.',
            'avatar': AVATARES_EJEMPLO[1]
        },
        {
            'nombre': 'Carlos Rodríguez',
            'email': 'carlos@ejemplo.com',
            'password': 'cliente123',
            'telefono': '+56 9 2345 6789',
            'direccion': 'Viña del Mar, Valparaíso',
            'bio': 'Coleccionista de prendas exclusivas.',
            'avatar': AVATARES_EJEMPLO[2]
        },
        {
            'nombre': 'Ana María Silva',
            'email': 'ana@ejemplo.com',
            'password': 'cliente123',
            'telefono': '+56 9 3456 7890',
            'direccion': 'Providencia, Santiago',
            'bio': 'Diseñadora de interiores, busca calidad y diseño.',
            'avatar': AVATARES_EJEMPLO[0]
        }
    ]
    
    usuarios_creados = 0
    for user_data in usuarios_test:
        existing = Usuario.query.filter_by(email=user_data['email']).first()
        if existing:
            print(f"        ℹ️  Usuario {user_data['email']} ya existe")
            continue
        
        usuario = Usuario(
            nombre=user_data['nombre'],
            email=user_data['email'],
            telefono=user_data['telefono'],
            direccion=user_data['direccion'],
            bio=user_data['bio'],
            avatar_url=user_data['avatar'],
            es_admin=False,
            notificaciones_stock=True,
            notificaciones_pedidos=True,
            tema_preferido='light',
            idioma='es',
            fecha_registro=datetime.utcnow()
        )
        usuario.set_password(user_data['password'])
        db.session.add(usuario)
        usuarios_creados += 1
        print(f"        ✓ Usuario creado: {user_data['nombre']} ({user_data['email']})")
    
    db.session.commit()
    print(f"     ✓ {usuarios_creados} usuarios de prueba creados")
    print("        🔑 Password para todos: cliente123")

def create_system_config():
    """Crear configuración inicial del sistema"""
    print("\n  ⚙️  Creando configuración del sistema...")
    
    configuraciones_default = [
        # Tienda
        {'clave': 'tienda_nombre', 'valor': 'ATELIER', 'tipo': 'text'},
        {'clave': 'tienda_email', 'valor': 'contacto@atelier.com', 'tipo': 'text'},
        {'clave': 'tienda_telefono', 'valor': '+56 9 1234 5678', 'tipo': 'text'},
        {'clave': 'tienda_direccion', 'valor': 'Av. Providencia 1234, Santiago', 'tipo': 'text'},
        {'clave': 'tienda_descripcion', 'valor': 'ATELIER - Alta costura y diseño exclusivo desde 2020.', 'tipo': 'text'},
        
        # Inventario
        {'clave': 'stock_alerta', 'valor': '5', 'tipo': 'number'},
        {'clave': 'productos_por_pagina', 'valor': '12', 'tipo': 'number'},
        {'clave': 'moneda', 'valor': 'CLP', 'tipo': 'text'},
        {'clave': 'simbolo_moneda', 'valor': '$', 'tipo': 'text'},
        
        # Apariencia
        {'clave': 'tema_default', 'valor': 'light', 'tipo': 'text'},
        {'clave': 'tipografia_titulos', 'valor': 'Noto Serif', 'tipo': 'text'},
        {'clave': 'color_acento', 'valor': '#745b3b', 'tipo': 'text'},
        
        # Sistema
        {'clave': 'ultima_actualizacion', 'valor': '15 de Marzo, 2026', 'tipo': 'text'},
        {'clave': 'version_sistema', 'valor': '2.1.0', 'tipo': 'text'},
    ]
    
    configs_creadas = 0
    for config_data in configuraciones_default:
        existing = ConfiguracionSistema.query.filter_by(clave=config_data['clave']).first()
        if existing:
            continue
        
        config = ConfiguracionSistema(**config_data)
        db.session.add(config)
        configs_creadas += 1
    
    db.session.commit()
    print(f"     ✓ {configs_creadas} configuraciones del sistema creadas")

def seed_database():
    """Poblar la base de datos con datos iniciales"""
    
    print("\n" + "="*60)
    print("🌱 ATELIER BOUTIQUE - Inicializando Base de Datos")
    print("="*60 + "\n")
    
    # 1. Crear directorios necesarios
    create_database_directory()
    
    # 2. Crear tablas
    init_database()
    
    # 3. Crear configuración del sistema
    create_system_config()
    
    # 4. Crear usuario administrador
    create_admin_user()
    
    # 5. Crear usuarios de prueba
    create_test_users()
    
    # 6. Limpiar datos existentes (excepto usuarios y configuración)
    print("\n  🧹 Limpiando datos de productos...")
    try:
        CarritoItem.query.delete()
        Producto.query.delete()
        Categoria.query.delete()
        db.session.commit()
        print("     ✓ Datos anteriores eliminados")
    except Exception as e:
        print(f"     ℹ️  No había datos previos para eliminar: {e}")
    
    # 7. Crear categorías
    print("\n  📁 Creando categorías...")
    categorias_data = [
        {'nombre': 'Pantalones', 'descripcion': 'Pantalones de diseño exclusivo con cortes precisos y telas premium.'},
        {'nombre': 'Poleras', 'descripcion': 'Poleras de algodón premium y cortes minimalistas para un estilo sofisticado.'},
        {'nombre': 'Chombas', 'descripcion': 'Chombas y sweaters de lana merino y cashmere de la más alta calidad.'},
        {'nombre': 'Chaquetas', 'descripcion': 'Chaquetas estructuradas, blazers y abrigos de diseño atemporal.'},
        {'nombre': 'Accesorios', 'descripcion': 'Accesorios de lujo para completar tu look con elegancia.'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria = Categoria(**cat_data)
        db.session.add(categoria)
        categorias[cat_data['nombre']] = categoria
    
    db.session.commit()
    print(f"     ✓ {len(categorias)} categorías creadas")
    
    # 8. Crear productos
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
        {'nombre': 'Gafas de Sol Vintage', 'categoria': 'Accesorios', 'precio': 120000, 'stock': 10, 'sku': 'AC-004'},
    ]
    
    producto_count = 0
    for idx, prod_data in enumerate(productos_data):
        categoria = categorias[prod_data['categoria']]
        imagenes_cat = IMAGENES_POR_CATEGORIA.get(prod_data['categoria'], IMAGENES_POR_CATEGORIA['Poleras'])
        imagen_url = imagenes_cat[idx % len(imagenes_cat)]
        
        # Descripciones más detalladas
        descripciones = {
            'Pantalones': 'Confeccionado con materiales premium y un corte que estiliza la figura.',
            'Poleras': 'Algodón de la más alta calidad, suave al tacto y con acabados impecables.',
            'Chombas': 'Tejido a mano con las mejores lanas, perfecto para los días fríos.',
            'Chaquetas': 'Diseño estructurado que eleva cualquier outfit con elegancia.',
            'Accesorios': 'El complemento perfecto para un look sofisticado y único.'
        }
        
        producto = Producto(
            nombre=prod_data['nombre'],
            descripcion=f"{prod_data['nombre']} de nuestra colección exclusiva. {descripciones.get(prod_data['categoria'], '')} Diseño atemporal que perdura en el tiempo.",
            precio=prod_data['precio'],
            stock=prod_data['stock'],
            sku=prod_data['sku'],
            imagen_url=imagen_url,
            categoria_id=categoria.id,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(producto)
        producto_count += 1
    
    db.session.commit()
    print(f"     ✓ {producto_count} productos creados")
    
    # 9. Crear items de carrito demo para cada usuario
    print("\n  🛒 Creando items de carrito de ejemplo...")
    
    productos = Producto.query.limit(4).all()
    usuarios = Usuario.query.filter(Usuario.es_admin == False).all()
    items_creados = 0
    
    for usuario in usuarios:
        for producto in productos[:2]:  # 2 productos por usuario
            if producto.stock > 0:
                item = CarritoItem(
                    session_id=f'user-{usuario.id}-session',
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
    print(f"   ├── Configuraciones del sistema: {ConfiguracionSistema.query.count()}")
    print(f"   ├── Usuarios: {Usuario.query.count()}")
    print(f"   │   ├── Administradores: {Usuario.query.filter_by(es_admin=True).count()}")
    print(f"   │   └── Clientes: {Usuario.query.filter_by(es_admin=False).count()}")
    print(f"   ├── Categorías: {Categoria.query.count()}")
    print(f"   ├── Productos: {Producto.query.count()}")
    print(f"   └── Items en carrito demo: {CarritoItem.query.count()}")
    
    total_stock = db.session.query(db.func.sum(Producto.stock)).scalar() or 0
    valor_inventario = db.session.query(db.func.sum(Producto.precio * Producto.stock)).scalar() or 0
    
    print(f"\n💰 Valor total del inventario: ${valor_inventario:,.0f}".replace(',', '.'))
    print(f"📦 Unidades totales en stock: {total_stock}")
    
    print("\n🔐 Credenciales de Acceso:")
    print("\n   👑 ADMINISTRADOR:")
    print("      📧 Email: admin@atelier.com")
    print("      🔑 Password: admin123")
    print("      👤 Perfil: Completo con preferencias")
    
    print("\n   👥 CLIENTES (Password: cliente123):")
    print("      📧 maria@ejemplo.com - María González")
    print("      📧 carlos@ejemplo.com - Carlos Rodríguez")
    print("      📧 ana@ejemplo.com - Ana María Silva")
    
    print("\n🔗 Accesos:")
    print("   🏠 Tienda: http://localhost:5000/")
    print("   🔐 Login: http://localhost:5000/login")
    print("   📊 Admin Dashboard: http://localhost:5000/admin/")
    
    print("\n🚀 ¡Listo! Ahora puedes ejecutar: python run.py\n")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()