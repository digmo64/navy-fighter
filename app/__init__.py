from flask import Flask
from app.models.database import init_db
from app.controllers.game_controller import game_controller
from app.controllers.routes_controller import web_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )
    app.secret_key = "navy-fighter-udistrital-2026"

    init_db()
    game_controller.inicializar_datos_base()
    app.register_blueprint(web_bp)
    return app