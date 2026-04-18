#!/usr/bin/env python3
"""
ATELIER Boutique - Punto de entrada de la aplicación Flask
Ejecutar con: python run.py
"""

import os
import sys

# Verificar que existe el directorio de templates
def check_project_structure():
    """Verifica que la estructura del proyecto esté correcta"""
    errors = []
    
    # Verificar directorios esenciales
    required_dirs = [
        'app/templates',
        'app/static',
        'app/database'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            if dir_path == 'app/database':
                os.makedirs(dir_path, exist_ok=True)
                print(f"📁 Creado directorio: {dir_path}")
            else:
                errors.append(f"❌ Falta directorio: {dir_path}")
    
    # Verificar templates esenciales
    required_templates = [
        'index.html',
        'admininventario.html',
        'catalogodesktop.html',
        'catalogomovil.html',
        'detallesdesktop.html',
        'detallesmovil.html',
        'carritodeskop.html',
        'carritomovil.html'
    ]
    
    for template in required_templates:
        if not os.path.exists(f'app/templates/{template}'):
            errors.append(f"❌ Falta template: {template}")
    
    if errors:
        print("\n⚠️  ADVERTENCIA: Faltan algunos archivos:\n")
        for error in errors:
            print(f"   {error}")
        print("\n   Algunas rutas pueden no funcionar correctamente.\n")
        return False
    
    return True

# Verificar estructura antes de importar
check_project_structure()

from app import create_app, db
from app.models.models import Categoria, Producto, CarritoItem

# Crear la aplicación
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Contexto para el shell de Flask"""
    return {
        'db': db,
        'Categoria': Categoria,
        'Producto': Producto,
        'CarritoItem': CarritoItem
    }

def check_database():
    """Verifica si la base de datos existe y tiene datos"""
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'database', 'boutique.db')
    
    if not os.path.exists(db_path):
        print("\n⚠️  ADVERTENCIA: Base de datos no encontrada.")
        print("   Ejecuta primero: python seed.py\n")
        return False
    
    # Verificar si hay productos
    try:
        with app.app_context():
            if Producto.query.count() == 0:
                print("\n⚠️  ADVERTENCIA: Base de datos vacía.")
                print("   Ejecuta: python seed.py para poblarla\n")
                return False
    except:
        pass
    
    return True

if __name__ == '__main__':
    print("\n" + "="*60)
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    ATELIER BOUTIQUE                          ║")
    print("║                   www.atelier.com                            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("="*60)
    
    # Verificar base de datos
    db_ok = check_database()
    
    # Obtener puerto del entorno (para Render/Heroku) o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    # Ejecutar la aplicación
    debug_mode = os.environ.get('FLASK_ENV') == 'development' or not os.environ.get('PRODUCTION')
    
    print(f"""
┌────────────────────────────────────────────────────────────────┐
│  🌐 Servidor: http://localhost:{port}                              │
│  🛍️  Tienda: http://localhost:{port}/                             │
│  🔧 Admin: http://localhost:{port}/admin                          │
│  🐛 Modo Debug: {'Activado' if debug_mode else 'Desactivado':<46}│
└────────────────────────────────────────────────────────────────┘
    """)
    
    if not db_ok:
        respuesta = input("¿Deseas ejecutar el seed ahora? (s/N): ")
        if respuesta.lower() == 's':
            print("\n🔄 Ejecutando seed.py...\n")
            os.system('python seed.py')
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)