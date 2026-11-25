from flask import Blueprint, render_template, request, jsonify
from app.controllers.game_controller import game_controller
from app.models.file_manager import FileManager
from app.models.database import db_session
from app.models.repositories import PartidaRepository

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template(
        "index.html",
        jugadores=game_controller.listar_jugadores(),
        flotas=game_controller.listar_flotas(),
        salas=game_controller.listar_salas_disponibles(),
        guardadas=FileManager.listar_partidas_guardadas(),
    )


@web_bp.route("/sala/<codigo>")
def vista_sala(codigo: str):
    jugador_id = request.args.get("jugador_id", type=int)
    return render_template("sala.html", codigo=codigo.upper(), jugador_id=jugador_id)


# --- API CRUD JUGADORES ---
@web_bp.route("/api/jugadores", methods=["GET", "POST"])
def api_jugadores():
    if request.method == "GET":
        return jsonify(game_controller.listar_jugadores())
    try:
        data = request.get_json(force=True)
        jugador = game_controller.crear_jugador(data.get("username", ""))
        return jsonify(jugador), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/jugadores/<int:jugador_id>", methods=["PUT", "DELETE"])
def api_jugador_detalle(jugador_id: int):
    try:
        if request.method == "PUT":
            data = request.get_json(force=True)
            return jsonify(game_controller.actualizar_jugador(jugador_id, data.get("username", "")))
        game_controller.eliminar_jugador(jugador_id)
        return jsonify({"mensaje": "Jugador eliminado"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- API CRUD FLOTAS ---
@web_bp.route("/api/flotas", methods=["GET", "POST"])
def api_flotas():
    if request.method == "GET":
        return jsonify(game_controller.listar_flotas())
    try:
        data = request.get_json(force=True)
        flota = game_controller.crear_flota(
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion", ""),
            tamano_tablero=int(data.get("tamano_tablero", 8)),
            barcos=data.get("barcos", []),
        )
        return jsonify(flota), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/flotas/<int:flota_id>", methods=["PUT", "DELETE"])
def api_flota_detalle(flota_id: int):
    try:
        if request.method == "PUT":
            data = request.get_json(force=True)
            flota = game_controller.actualizar_flota(
                flota_id=flota_id,
                nombre=data.get("nombre", ""),
                descripcion=data.get("descripcion", ""),
                tamano_tablero=int(data.get("tamano_tablero", 8)),
                barcos=data.get("barcos", []),
            )
            return jsonify(flota)
        game_controller.eliminar_flota(flota_id)
        return jsonify({"mensaje": "Plantilla eliminada"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- API MULTIJUGADOR Y PARTIDAS ---
@web_bp.route("/api/salas", methods=["POST"])
def api_crear_sala():
    try:
        data = request.get_json(force=True)
        vista = game_controller.crear_sala(int(data["jugador_id"]), int(data["flota_id"]))
        return jsonify(vista), 201
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/salas/<codigo>/unirse", methods=["POST"])
def api_unirse_sala(codigo: str):
    try:
        data = request.get_json(force=True)
        vista = game_controller.unirse_sala(codigo, int(data["jugador_id"]))
        return jsonify(vista)
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/salas/<codigo>/estado", methods=["GET"])
def api_estado_sala(codigo: str):
    try:
        jugador_id = request.args.get("jugador_id", type=int)
        return jsonify(game_controller.obtener_estado_sala(codigo, jugador_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@web_bp.route("/api/salas/<codigo>/desplegar", methods=["POST"])
def api_desplegar(codigo: str):
    try:
        data = request.get_json(force=True)
        vista = game_controller.desplegar_flota(codigo, int(data["jugador_id"]), data.get("ubicaciones"))
        return jsonify(vista)
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/salas/<codigo>/disparar", methods=["POST"])
def api_disparar(codigo: str):
    try:
        data = request.get_json(force=True)
        resp = game_controller.ejecutar_disparo(codigo, int(data["jugador_id"]), int(data["fila"]), int(data["col"]))
        return jsonify(resp)
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/salas/<codigo>/guardar", methods=["POST"])
def api_guardar_partida(codigo: str):
    try:
        ruta = game_controller.guardar_partida(codigo)
        return jsonify({"mensaje": f"Partida serializada en {ruta}"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@web_bp.route("/api/salas/<codigo>/reanudar", methods=["POST"])
def api_reanudar_partida(codigo: str):
    try:
        vista = game_controller.reanudar_partida(codigo)
        return jsonify(vista)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@web_bp.route("/api/exportar-csv", methods=["POST"])
def api_exportar_csv():
    msg = game_controller.encolar_exportacion_csv()
    return jsonify({"mensaje": msg, "ultimo_archivo": game_controller.worker_csv.ultimo_reporte})


@web_bp.route("/api/historial", methods=["GET"])
def api_historial():
    session = db_session()
    try:
        partidas = PartidaRepository(session).listar_historial()
        return jsonify([
            {
                "codigo": p.codigo_sala,
                "estado": p.estado,
                "jugador1_id": p.jugador1_id,
                "jugador2_id": p.jugador2_id,
                "ganador_id": p.ganador_id,
            }
            for p in partidas
        ])
    finally:
        db_session.remove()