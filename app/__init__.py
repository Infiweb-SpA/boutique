from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
# Ahora la ruta de login pertenece al blueprint 'auth'
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder al panel de administración.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Filtro personalizado para formatear precios
    @app.template_filter('clp')
    def format_clp(value):
        try:
            formatted = "{:,.0f}".format(float(value)).replace(',', '.')
            return f"${formatted}"
        except (ValueError, TypeError):
            return value

    # Context processor para tener el contador del carrito disponible en todos los templates
    @app.context_processor
    def utility_processor():
        from flask import session
        from app.models import CarritoItem
        import uuid

        def get_cart_count():
            if 'cart_session_id' in session:
                session_id = session['cart_session_id']
                count = CarritoItem.query.filter_by(session_id=session_id).count()
                return count
            return 0

        return dict(cart_count=get_cart_count)

    # Registrar los blueprints desde la función definida en app/routes/__init__.py
    from app.routes import register_blueprints
    register_blueprints(app)

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario
    return Usuario.query.get(int(user_id))