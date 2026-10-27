from flask import Flask

def create_app():
    # Le indicamos a Flask dónde están las vistas (HTML)
    app = Flask(__name__, template_folder='views/templates')
    
    # Registramos las rutas
    from app.routes import main
    app.register_blueprint(main)
    
    return app