import random
from app.domain.barcos import Barco


class Tablero:
    def __init__(self, tamano: int = 8):
        self.tamano = tamano
        self.barcos: list[Barco] = []
        self.disparos_recibidos: dict[tuple[int, int], str] = {}

    def _calcular_coordenadas(self, fila: int, col: int, tamano: int, orientacion: str) -> list[tuple[int, int]]:
        coords = []
        for i in range(tamano):
            r = fila + (i if orientacion == "V" else 0)
            c = col + (i if orientacion == "H" else 0)
            if not (0 <= r < self.tamano and 0 <= c < self.tamano):
                raise ValueError("La embarcación se sale de los límites del tablero.")
            coords.append((r, c))
        return coords

    def _hay_colision(self, nuevas_coords: list[tuple[int, int]]) -> bool:
        ocupadas = {pos for b in self.barcos for pos in b.coordenadas}
        return any(pos in ocupadas for pos in nuevas_coords)

    def colocar_flota_manual(self, flota: list[Barco], ubicaciones: list[dict]) -> None:
        if len(flota) != len(ubicaciones):
            raise ValueError("La cantidad de ubicaciones no coincide con los barcos de la flota.")

        self.barcos.clear()
        self.disparos_recibidos.clear()

        for barco, ub in zip(flota, ubicaciones):
            fila = int(ub["fila"])
            col = int(ub["col"])
            orientacion = ub["orientacion"].upper()
            if orientacion not in ("H", "V"):
                raise ValueError("Orientación inválida. Use 'H' o 'V'.")
            coords = self._calcular_coordenadas(fila, col, barco.tamano, orientacion)
            if self._hay_colision(coords):
                raise ValueError(f"Superposición detectada al ubicar {barco.nombre}.")
            barco.asignar_coordenadas(coords)
            self.barcos.append(barco)

    def colocar_flota_aleatoria(self, flota: list[Barco]) -> None:
        self.barcos.clear()
        self.disparos_recibidos.clear()
        for barco in flota:
            colocado = False
            for _ in range(200):
                orientacion = random.choice(["H", "V"])
                fila = random.randint(0, self.tamano - 1)
                col = random.randint(0, self.tamano - 1)
                try:
                    coords = self._calcular_coordenadas(fila, col, barco.tamano, orientacion)
                    if not self._hay_colision(coords):
                        barco.asignar_coordenadas(coords)
                        self.barcos.append(barco)
                        colocado = True
                        break
                except ValueError:
                    continue
            if not colocado:
                raise RuntimeError(f"No fue posible ubicar automáticamente {barco.nombre}.")

    def recibir_disparo(self, fila: int, col: int) -> dict:
        if not (0 <= fila < self.tamano and 0 <= col < self.tamano):
            raise ValueError("Coordenada fuera del tablero.")
        pos = (fila, col)
        if pos in self.disparos_recibidos:
            raise ValueError("Ya se disparó a esta coordenada.")

        for barco in self.barcos:
            if barco.recibir_impacto(fila, col):
                hundido = barco.esta_hundido()
                resultado = "HUNDIDO" if hundido else "IMPACTO"
                self.disparos_recibidos[pos] = resultado
                return {
                    "resultado": resultado,
                    "barco": barco.nombre if hundido else None,
                    "puntos": barco.puntos_base + (barco.bono_hundimiento() if hundido else 0),
                }

        self.disparos_recibidos[pos] = "AGUA"
        return {"resultado": "AGUA", "barco": None, "puntos": 0}

    def todos_hundidos(self) -> bool:
        return len(self.barcos) > 0 and all(b.esta_hundido() for b in self.barcos)

    def vista_propia(self) -> list[list[str]]:
        matriz = [["AGUA" for _ in range(self.tamano)] for _ in range(self.tamano)]
        for barco in self.barcos:
            for r, c in barco.coordenadas:
                matriz[r][c] = "BARCO"
        for (r, c), estado in self.disparos_recibidos.items():
            matriz[r][c] = "TOCADO" if estado in ("IMPACTO", "HUNDIDO") else "FALLO"
        return matriz

    def vista_enemiga(self) -> list[list[str]]:
        matriz = [["OCULTO" for _ in range(self.tamano)] for _ in range(self.tamano)]
        for (r, c), estado in self.disparos_recibidos.items():
            matriz[r][c] = "TOCADO" if estado in ("IMPACTO", "HUNDIDO") else "FALLO"
        return matriz