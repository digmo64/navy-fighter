from flask import Flask
from app.persistence.database import init_db
from app.services.game_service import game_service
from app.interface.routes import web_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "navy-fighter-udistrital-2026"

    init_db()
    game_service.inicializar_datos_base()
    app.register_blueprint(web_bp)
    return app