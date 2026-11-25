import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.db_models import Jugador, PlantillaFlota, PartidaDB, MovimientoDB


class JugadorRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, username: str) -> Jugador:
        jugador = Jugador(username=username.strip())
        self.session.add(jugador)
        self.session.commit()
        return jugador

    def listar_todos(self) -> list[Jugador]:
        return self.session.query(Jugador).order_by(Jugador.victorias.desc(), Jugador.id.asc()).all()

    def obtener_por_id(self, jugador_id: int) -> Jugador | None:
        return self.session.query(Jugador).filter_by(id=jugador_id).first()

    def obtener_por_username(self, username: str) -> Jugador | None:
        return self.session.query(Jugador).filter_by(username=username.strip()).first()

    def actualizar_nombre(self, jugador_id: int, nuevo_username: str) -> Jugador:
        jugador = self.obtener_por_id(jugador_id)
        if not jugador:
            raise ValueError("Jugador no encontrado.")
        jugador.username = nuevo_username.strip()
        self.session.commit()
        return jugador

    def eliminar(self, jugador_id: int) -> None:
        jugador = self.obtener_por_id(jugador_id)
        if not jugador:
            raise ValueError("Jugador no encontrado.")
        self.session.delete(jugador)
        self.session.commit()

    def registrar_disparo(self, jugador_id: int, acierto: bool) -> None:
        jugador = self.obtener_por_id(jugador_id)
        if jugador:
            jugador.disparos_totales += 1
            if acierto:
                jugador.aciertos_totales += 1
            self.session.commit()

    def registrar_resultado_partida(self, jugador1_id: int, jugador2_id: int | None, ganador_id: int | None) -> None:
        for jid in (jugador1_id, jugador2_id):
            if jid:
                j = self.obtener_por_id(jid)
                if j:
                    j.partidas_jugadas += 1
                    if ganador_id == jid:
                        j.victorias += 1
        self.session.commit()


class FlotaRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre: str, descripcion: str, tamano_tablero: int, barcos: list[dict]) -> PlantillaFlota:
        flota = PlantillaFlota(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            tamano_tablero=int(tamano_tablero),
            configuracion_json=json.dumps(barcos, ensure_ascii=False),
        )
        self.session.add(flota)
        self.session.commit()
        return flota

    def listar_todas(self) -> list[PlantillaFlota]:
        return self.session.query(PlantillaFlota).order_by(PlantillaFlota.id.asc()).all()

    def obtener_por_id(self, flota_id: int) -> PlantillaFlota | None:
        return self.session.query(PlantillaFlota).filter_by(id=flota_id).first()

    def actualizar(self, flota_id: int, nombre: str, descripcion: str, tamano_tablero: int, barcos: list[dict]) -> PlantillaFlota:
        flota = self.obtener_por_id(flota_id)
        if not flota:
            raise ValueError("Plantilla de flota no encontrada.")
        flota.nombre = nombre.strip()
        flota.descripcion = descripcion.strip()
        flota.tamano_tablero = int(tamano_tablero)
        flota.configuracion_json = json.dumps(barcos, ensure_ascii=False)
        self.session.commit()
        return flota

    def eliminar(self, flota_id: int) -> None:
        flota = self.obtener_por_id(flota_id)
        if not flota:
            raise ValueError("Plantilla de flota no encontrada.")
        self.session.delete(flota)
        self.session.commit()


class PartidaRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear_registro(self, codigo_sala: str, jugador1_id: int) -> PartidaDB:
        registro = PartidaDB(codigo_sala=codigo_sala, jugador1_id=jugador1_id, estado="ESPERANDO_RIVAL")
        self.session.add(registro)
        self.session.commit()
        return registro

    def obtener_por_codigo(self, codigo_sala: str) -> PartidaDB | None:
        return self.session.query(PartidaDB).filter_by(codigo_sala=codigo_sala).order_by(PartidaDB.id.desc()).first()

    def actualizar_estado(self, codigo_sala: str, estado: str, jugador2_id: int | None = None, ganador_id: int | None = None) -> None:
        registro = self.obtener_por_codigo(codigo_sala)
        if not registro:
            return
        registro.estado = estado
        if jugador2_id is not None:
            registro.jugador2_id = jugador2_id
        if ganador_id is not None:
            registro.ganador_id = ganador_id
            registro.fecha_fin = datetime.utcnow()
        self.session.commit()

    def registrar_movimiento(self, codigo_sala: str, jugador_id: int, fila: int, col: int, resultado: str, turno: int) -> None:
        registro = self.obtener_por_codigo(codigo_sala)
        if not registro:
            return
        mov = MovimientoDB(
            partida_id=registro.id,
            jugador_id=jugador_id,
            fila=fila,
            columna=col,
            resultado=resultado,
            turno_numero=turno,
        )
        self.session.add(mov)
        self.session.commit()

    def listar_historial(self, limite: int = 15) -> list[PartidaDB]:
        return self.session.query(PartidaDB).order_by(PartidaDB.id.desc()).limit(limite).all()