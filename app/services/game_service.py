import queue
import random
import string
import threading
import time
from app.domain.partida import PartidaJuego
from app.persistence.database import db_session
from app.persistence.repositories import JugadorRepository, FlotaRepository, PartidaRepository
from app.persistence.file_manager import FileManager
from app.services.concurrency import MonitorSalasThread, ExportadorCSVWorker


class GameService:
    def __init__(self):
        self.salas_activas: dict[str, PartidaJuego] = {}
        self._lock = threading.Lock()
        self.cola_exportacion: queue.Queue = queue.Queue()

        self.worker_csv = ExportadorCSVWorker(self.cola_exportacion)
        self.worker_csv.start()

        self.monitor_salas = MonitorSalasThread(self)
        self.monitor_salas.start()

    def inicializar_datos_base(self) -> None:
        session = db_session()
        try:
            flota_repo = FlotaRepository(session)
            if not flota_repo.listar_todas():
                for item in FileManager.leer_flotas_iniciales():
                    flota_repo.crear(
                        nombre=item["nombre"],
                        descripcion=item.get("descripcion", ""),
                        tamano_tablero=item.get("tamano_tablero", 8),
                        barcos=item["barcos"],
                    )
        finally:
            db_session.remove()

    def _generar_codigo_sala(self) -> str:
        while True:
            codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if codigo not in self.salas_activas:
                return codigo

    # --- CRUD JUGADORES ---
    def listar_jugadores(self) -> list[dict]:
        session = db_session()
        try:
            return [j.to_dict() for j in JugadorRepository(session).listar_todos()]
        finally:
            db_session.remove()

    def crear_jugador(self, username: str) -> dict:
        if not username or not username.strip():
            raise ValueError("El nombre de usuario es obligatorio.")
        session = db_session()
        try:
            repo = JugadorRepository(session)
            if repo.obtener_por_username(username):
                raise ValueError("Ese nombre de jugador ya existe.")
            return repo.crear(username).to_dict()
        finally:
            db_session.remove()

    def actualizar_jugador(self, jugador_id: int, username: str) -> dict:
        if not username or not username.strip():
            raise ValueError("El nuevo nombre es obligatorio.")
        session = db_session()
        try:
            return JugadorRepository(session).actualizar_nombre(jugador_id, username).to_dict()
        finally:
            db_session.remove()

    def eliminar_jugador(self, jugador_id: int) -> None:
        session = db_session()
        try:
            JugadorRepository(session).eliminar(jugador_id)
        finally:
            db_session.remove()

    # --- CRUD PLANTILLAS DE FLOTA ---
    def listar_flotas(self) -> list[dict]:
        session = db_session()
        try:
            return [f.to_dict() for f in FlotaRepository(session).listar_todas()]
        finally:
            db_session.remove()

    def crear_flota(self, nombre: str, descripcion: str, tamano_tablero: int, barcos: list[dict]) -> dict:
        if not nombre or not barcos:
            raise ValueError("Nombre y lista de barcos son obligatorios.")
        session = db_session()
        try:
            return FlotaRepository(session).crear(nombre, descripcion, tamano_tablero, barcos).to_dict()
        finally:
            db_session.remove()

    def actualizar_flota(self, flota_id: int, nombre: str, descripcion: str, tamano_tablero: int, barcos: list[dict]) -> dict:
        session = db_session()
        try:
            return FlotaRepository(session).actualizar(flota_id, nombre, descripcion, tamano_tablero, barcos).to_dict()
        finally:
            db_session.remove()

    def eliminar_flota(self, flota_id: int) -> None:
        session = db_session()
        try:
            FlotaRepository(session).eliminar(flota_id)
        finally:
            db_session.remove()

    # --- GESTIÓN DE SALAS MULTIJUGADOR ---
    def crear_sala(self, jugador_id: int, flota_id: int) -> dict:
        session = db_session()
        try:
            jugador = JugadorRepository(session).obtener_por_id(jugador_id)
            flota = FlotaRepository(session).obtener_por_id(flota_id)
            if not jugador or not flota:
                raise ValueError("Jugador o plantilla de flota inválidos.")

            flota_dict = flota.to_dict()
            with self._lock:
                codigo = self._generar_codigo_sala()
                partida = PartidaJuego(
                    codigo=codigo,
                    nombre_flota=flota_dict["nombre"],
                    tamano_tablero=flota_dict["tamano_tablero"],
                    config_barcos=flota_dict["barcos"],
                )
                partida.registrar_jugador(jugador.id, jugador.username)
                self.salas_activas[codigo] = partida

            PartidaRepository(session).crear_registro(codigo, jugador.id)
            return partida.serializar_vista(jugador.id)
        finally:
            db_session.remove()

    def unirse_sala(self, codigo: str, jugador_id: int) -> dict:
        codigo = codigo.strip().upper()
        session = db_session()
        try:
            jugador = JugadorRepository(session).obtener_por_id(jugador_id)
            if not jugador:
                raise ValueError("Jugador no encontrado.")

            with self._lock:
                partida = self.salas_activas.get(codigo)
                if not partida:
                    raise ValueError("Sala no encontrada o ya finalizada.")
                partida.unirse(jugador.id, jugador.username)
                estado_actual = partida.estado.nombre
                vista = partida.serializar_vista(jugador.id)

            PartidaRepository(session).actualizar_estado(codigo, estado_actual, jugador2_id=jugador.id)
            return vista
        finally:
            db_session.remove()

    def desplegar_flota(self, codigo: str, jugador_id: int, ubicaciones: list[dict] | None) -> dict:
        codigo = codigo.strip().upper()
        session = db_session()
        try:
            with self._lock:
                partida = self.salas_activas.get(codigo)
                if not partida:
                    raise ValueError("Sala no encontrada.")
                partida.desplegar(jugador_id, ubicaciones)
                estado_actual = partida.estado.nombre
                vista = partida.serializar_vista(jugador_id)

            PartidaRepository(session).actualizar_estado(codigo, estado_actual)
            return vista
        finally:
            db_session.remove()

    def ejecutar_disparo(self, codigo: str, jugador_id: int, fila: int, col: int) -> dict:
        codigo = codigo.strip().upper()
        session = db_session()
        try:
            with self._lock:
                partida = self.salas_activas.get(codigo)
                if not partida:
                    raise ValueError("Sala no encontrada.")
                resultado = partida.disparar(jugador_id, fila, col)
                estado_actual = partida.estado.nombre
                ganador_id = partida.ganador_id
                turno = partida.numero_turno
                jugadores_ids = list(partida.jugadores.keys())
                vista = partida.serializar_vista(jugador_id)

            j_repo = JugadorRepository(session)
            p_repo = PartidaRepository(session)
            j_repo.registrar_disparo(jugador_id, resultado["resultado"] in ("IMPACTO", "HUNDIDO"))
            p_repo.registrar_movimiento(codigo, jugador_id, fila, col, resultado["resultado"], turno)

            if estado_actual == "FINALIZADO":
                p_repo.actualizar_estado(codigo, estado_actual, ganador_id=ganador_id)
                j2 = jugadores_ids[1] if len(jugadores_ids) > 1 else None
                j_repo.registrar_resultado_partida(jugadores_ids[0], j2, ganador_id)

            return {"disparo": resultado, "estado_sala": vista}
        finally:
            db_session.remove()

    def obtener_estado_sala(self, codigo: str, jugador_id: int) -> dict:
        with self._lock:
            partida = self.salas_activas.get(codigo.strip().upper())
            if not partida:
                raise ValueError("Sala no encontrada.")
            return partida.serializar_vista(jugador_id)

    def listar_salas_disponibles(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "codigo": p.codigo,
                    "estado": p.estado.nombre,
                    "flota": p.nombre_flota,
                    "jugadores": list(p.jugadores.values()),
                }
                for p in self.salas_activas.values()
                if p.estado.nombre != "FINALIZADO"
            ]

    # --- SERIALIZACIÓN Y EXPORTACIÓN ASÍNCRONA ---
    def guardar_partida(self, codigo: str) -> str:
        with self._lock:
            partida = self.salas_activas.get(codigo.strip().upper())
            if not partida:
                raise ValueError("Sala no encontrada.")
            return FileManager.guardar_partida_serializada(partida)

    def reanudar_partida(self, codigo: str) -> dict:
        partida = FileManager.cargar_partida_serializada(codigo)
        with self._lock:
            self.salas_activas[partida.codigo] = partida
            primer_jugador = next(iter(partida.jugadores.keys()))
            return partida.serializar_vista(primer_jugador)

    def encolar_exportacion_csv(self) -> str:
        datos = self.listar_jugadores()
        self.cola_exportacion.put({"tipo": "EXPORTAR_RANKING", "datos": datos})
        return "Exportación CSV encolada en segundo plano."

    def verificar_inactividad_salas(self, timeout_segundos: int) -> None:
        ahora = time.time()
        with self._lock:
            for partida in self.salas_activas.values():
                if partida.estado.nombre == "EN_CURSO" and (ahora - partida.ultima_actividad) > timeout_segundos:
                    ganador = partida.obtener_rival_id(partida.turno_actual_id)
                    partida.forzar_victoria_por_abandono(
                        ganador,
                        "Tiempo de turno excedido. Victoria asignada automáticamente.",
                    )


game_service = GameService()