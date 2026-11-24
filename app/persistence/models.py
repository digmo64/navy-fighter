from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.persistence.database import Base


class Jugador(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    partidas_jugadas = Column(Integer, default=0)
    victorias = Column(Integer, default=0)
    disparos_totales = Column(Integer, default=0)
    aciertos_totales = Column(Integer, default=0)
    creado_en = Column(DateTime, default=datetime.utcnow)

    def precision(self) -> float:
        if self.disparos_totales == 0:
            return 0.0
        return round((self.aciertos_totales / self.disparos_totales) * 100, 1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "partidas_jugadas": self.partidas_jugadas,
            "victorias": self.victorias,
            "disparos_totales": self.disparos_totales,
            "aciertos_totales": self.aciertos_totales,
            "precision": self.precision(),
        }


class PlantillaFlota(Base):
    __tablename__ = "plantillas_flota"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), unique=True, nullable=False)
    descripcion = Column(String(200), default="")
    tamano_tablero = Column(Integer, default=8)
    configuracion_json = Column(Text, nullable=False)

    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "tamano_tablero": self.tamano_tablero,
            "barcos": json.loads(self.configuracion_json),
        }


class PartidaDB(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_sala = Column(String(12), nullable=False)
    jugador1_id = Column(Integer, ForeignKey("jugadores.id"), nullable=False)
    jugador2_id = Column(Integer, ForeignKey("jugadores.id"), nullable=True)
    ganador_id = Column(Integer, ForeignKey("jugadores.id"), nullable=True)
    estado = Column(String(30), default="ESPERANDO_RIVAL")
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)

    movimientos = relationship("MovimientoDB", back_populates="partida", cascade="all, delete-orphan")


class MovimientoDB(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    partida_id = Column(Integer, ForeignKey("partidas.id"), nullable=False)
    jugador_id = Column(Integer, ForeignKey("jugadores.id"), nullable=False)
    fila = Column(Integer, nullable=False)
    columna = Column(Integer, nullable=False)
    resultado = Column(String(20), nullable=False)
    turno_numero = Column(Integer, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    partida = relationship("PartidaDB", back_populates="movimientos")