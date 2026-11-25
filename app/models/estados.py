from abc import ABC, abstractmethod


class EstadoPartida(ABC):
    @property
    @abstractmethod
    def nombre(self) -> str:
        pass

    def unirse(self, partida, jugador_id: int, username: str) -> None:
        raise ValueError(f"No es posible unirse cuando la partida está en estado {self.nombre}.")

    def desplegar_flota(self, partida, jugador_id: int, ubicaciones: list[dict] | None) -> None:
        raise ValueError(f"No es posible desplegar flota en estado {self.nombre}.")

    def disparar(self, partida, jugador_id: int, fila: int, col: int) -> dict:
        raise ValueError(f"No es posible disparar en estado {self.nombre}.")


class EstadoEsperandoRival(EstadoPartida):
    @property
    def nombre(self) -> str:
        return "ESPERANDO_RIVAL"

    def unirse(self, partida, jugador_id: int, username: str) -> None:
        if jugador_id in partida.jugadores:
            return
        if len(partida.jugadores) >= 2:
            raise ValueError("La sala ya está completa.")
        partida.registrar_jugador(jugador_id, username)
        if len(partida.jugadores) == 2:
            partida.cambiar_estado(EstadoDespliegue())


class EstadoDespliegue(EstadoPartida):
    @property
    def nombre(self) -> str:
        return "DESPLIEGUE"

    def desplegar_flota(self, partida, jugador_id: int, ubicaciones: list[dict] | None) -> None:
        if jugador_id not in partida.jugadores:
            raise ValueError("El jugador no pertenece a esta sala.")
        tablero = partida.tableros[jugador_id]
        flota = partida.construir_flota_jugador()
        if ubicaciones:
            tablero.colocar_flota_manual(flota, ubicaciones)
        else:
            tablero.colocar_flota_aleatoria(flota)

        partida.flotas_listas[jugador_id] = True
        if len(partida.flotas_listas) == 2 and all(partida.flotas_listas.values()):
            ids = list(partida.jugadores.keys())
            partida.turno_actual_id = ids[0]
            partida.cambiar_estado(EstadoEnCurso())


class EstadoEnCurso(EstadoPartida):
    @property
    def nombre(self) -> str:
        return "EN_CURSO"

    def disparar(self, partida, jugador_id: int, fila: int, col: int) -> dict:
        if jugador_id != partida.turno_actual_id:
            raise ValueError("Aún no es tu turno.")

        rival_id = partida.obtener_rival_id(jugador_id)
        tablero_rival = partida.tableros[rival_id]
        resultado = tablero_rival.recibir_disparo(fila, col)

        partida.numero_turno += 1
        partida.registrar_evento(
            f"Turno {partida.numero_turno}: {partida.jugadores[jugador_id]} disparó a ({fila + 1},{col + 1}) -> {resultado['resultado']}"
        )

        if tablero_rival.todos_hundidos():
            partida.ganador_id = jugador_id
            partida.cambiar_estado(EstadoFinalizado())
        else:
            partida.turno_actual_id = rival_id

        return resultado


class EstadoFinalizado(EstadoPartida):
    @property
    def nombre(self) -> str:
        return "FINALIZADO"