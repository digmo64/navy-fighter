import time
from app.domain.barcos import FlotaFactory, Barco
from app.domain.tablero import Tablero
from app.domain.estados import EstadoPartida, EstadoEsperandoRival


class PartidaJuego:
    def __init__(self, codigo: str, nombre_flota: str, tamano_tablero: int, config_barcos: list[dict]):
        self.codigo = codigo
        self.nombre_flota = nombre_flota
        self.tamano_tablero = tamano_tablero
        self.config_barcos = config_barcos
        self.jugadores: dict[int, str] = {}
        self.tableros: dict[int, Tablero] = {}
        self.flotas_listas: dict[int, bool] = {}
        self.turno_actual_id: int | None = None
        self.ganador_id: int | None = None
        self.numero_turno: int = 0
        self.bitacora: list[str] = []
        self.estado: EstadoPartida = EstadoEsperandoRival()
        self.ultima_actividad: float = time.time()

    def registrar_jugador(self, jugador_id: int, username: str) -> None:
        self.jugadores[jugador_id] = username
        self.tableros[jugador_id] = Tablero(self.tamano_tablero)
        self.flotas_listas[jugador_id] = False
        self.registrar_evento(f"{username} ingresó a la sala {self.codigo}.")

    def construir_flota_jugador(self) -> list[Barco]:
        return FlotaFactory.crear_flota_desde_config(self.config_barcos)

    def cambiar_estado(self, nuevo_estado: EstadoPartida) -> None:
        self.estado = nuevo_estado
        self.ultima_actividad = time.time()
        self.registrar_evento(f"Estado de sala cambiado a {nuevo_estado.nombre}.")

    def registrar_evento(self, mensaje: str) -> None:
        self.ultima_actividad = time.time()
        self.bitacora.append(mensaje)
        if len(self.bitacora) > 25:
            self.bitacora.pop(0)

    def obtener_rival_id(self, jugador_id: int) -> int:
        for jid in self.jugadores:
            if jid != jugador_id:
                return jid
        raise ValueError("Aún no hay rival en la sala.")

    def unirse(self, jugador_id: int, username: str) -> None:
        self.estado.unirse(self, jugador_id, username)

    def desplegar(self, jugador_id: int, ubicaciones: list[dict] | None = None) -> None:
        self.estado.desplegar_flota(self, jugador_id, ubicaciones)

    def disparar(self, jugador_id: int, fila: int, col: int) -> dict:
        return self.estado.disparar(self, jugador_id, fila, col)

    def forzar_victoria_por_abandono(self, ganador_id: int, motivo: str) -> None:
        from app.domain.estados import EstadoFinalizado
        self.ganador_id = ganador_id
        self.registrar_evento(motivo)
        self.cambiar_estado(EstadoFinalizado())

    def serializar_vista(self, jugador_id: int) -> dict:
        rival_id = next((jid for jid in self.jugadores if jid != jugador_id), None)
        tablero_propio = self.tableros[jugador_id].vista_propia() if jugador_id in self.tableros else []
        tablero_rival = self.tableros[rival_id].vista_enemiga() if rival_id and rival_id in self.tableros else []

        return {
            "codigo": self.codigo,
            "estado": self.estado.nombre,
            "tamano_tablero": self.tamano_tablero,
            "nombre_flota": self.nombre_flota,
            "config_barcos": self.config_barcos,
            "jugadores": self.jugadores,
            "flota_lista": self.flotas_listas.get(jugador_id, False),
            "rival_listo": self.flotas_listas.get(rival_id, False) if rival_id else False,
            "turno_actual_id": self.turno_actual_id,
            "es_mi_turno": self.turno_actual_id == jugador_id,
            "ganador_id": self.ganador_id,
            "ganador_nombre": self.jugadores.get(self.ganador_id) if self.ganador_id else None,
            "tablero_propio": tablero_propio,
            "tablero_rival": tablero_rival,
            "bitacora": self.bitacora[-8:],
        }