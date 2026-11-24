from abc import ABC, abstractmethod


class Barco(ABC):
    def __init__(self, nombre: str, tamano: int, puntos_base: int):
        self.nombre = nombre
        self.tamano = tamano
        self.puntos_base = puntos_base
        self.coordenadas: list[tuple[int, int]] = []
        self.impactos: set[tuple[int, int]] = set()

    @property
    def tipo(self) -> str:
        return self.__class__.__name__.lower()

    def asignar_coordenadas(self, coords: list[tuple[int, int]]) -> None:
        if len(coords) != self.tamano:
            raise ValueError(f"{self.nombre} requiere exactamente {self.tamano} casillas.")
        self.coordenadas = list(coords)
        self.impactos.clear()

    def recibir_impacto(self, fila: int, col: int) -> bool:
        pos = (fila, col)
        if pos in self.coordenadas:
            self.impactos.add(pos)
            return True
        return False

    def esta_hundido(self) -> bool:
        return len(self.coordenadas) > 0 and len(self.impactos) >= self.tamano

    @abstractmethod
    def bono_hundimiento(self) -> int:
        pass

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "nombre": self.nombre,
            "tamano": self.tamano,
            "coordenadas": [list(c) for c in self.coordenadas],
            "impactos": [list(i) for i in self.impactos],
            "hundido": self.esta_hundido(),
        }


class Portaaviones(Barco):
    def __init__(self):
        super().__init__("Portaaviones", 4, 100)

    def bono_hundimiento(self) -> int:
        return 50


class Acorazado(Barco):
    def __init__(self):
        super().__init__("Acorazado", 3, 80)

    def bono_hundimiento(self) -> int:
        return 35


class Submarino(Barco):
    def __init__(self):
        super().__init__("Submarino", 3, 75)

    def bono_hundimiento(self) -> int:
        return 30


class Destructor(Barco):
    def __init__(self):
        super().__init__("Destructor", 2, 50)

    def bono_hundimiento(self) -> int:
        return 20


class FlotaFactory:
    _CATALOGO = {
        "portaaviones": Portaaviones,
        "acorazado": Acorazado,
        "submarino": Submarino,
        "destructor": Destructor,
    }

    @classmethod
    def crear_barco(cls, tipo: str) -> Barco:
        clase = cls._CATALOGO.get(tipo.strip().lower())
        if not clase:
            raise ValueError(f"Tipo de barco no soportado: {tipo}")
        return clase()

    @classmethod
    def crear_flota_desde_config(cls, config_barcos: list[dict]) -> list[Barco]:
        flota = []
        for item in config_barcos:
            tipo = item["tipo"]
            cantidad = int(item.get("cantidad", 1))
            for _ in range(cantidad):
                flota.append(cls.crear_barco(tipo))
        return flota