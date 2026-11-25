import csv
import json
import os
import pickle
from datetime import datetime
from app.models.partida import PartidaJuego


class FileManager:
    INPUT_FLOTAS = os.path.join("data", "input", "flotas_default.json")
    SAVES_DIR = os.path.join("data", "saves")
    OUTPUT_DIR = os.path.join("data", "output")

    @classmethod
    def asegurar_directorios(cls) -> None:
        os.makedirs(os.path.dirname(cls.INPUT_FLOTAS), exist_ok=True)
        os.makedirs(cls.SAVES_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

    @classmethod
    def leer_flotas_iniciales(cls) -> list[dict]:
        cls.asegurar_directorios()
        if not os.path.exists(cls.INPUT_FLOTAS):
            return []
        with open(cls.INPUT_FLOTAS, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def guardar_partida_serializada(cls, partida: PartidaJuego) -> str:
        cls.asegurar_directorios()
        ruta_pkl = os.path.join(cls.SAVES_DIR, f"{partida.codigo}.pkl")
        ruta_json = os.path.join(cls.SAVES_DIR, f"{partida.codigo}.json")

        with open(ruta_pkl, "wb") as f_pkl:
            pickle.dump(partida, f_pkl)

        resumen = {
            "codigo": partida.codigo,
            "estado": partida.estado.nombre,
            "jugadores": partida.jugadores,
            "turno_actual_id": partida.turno_actual_id,
            "numero_turno": partida.numero_turno,
            "guardado_en": datetime.now().isoformat(),
        }
        with open(ruta_json, "w", encoding="utf-8") as f_json:
            json.dump(resumen, f_json, indent=2, ensure_ascii=False)

        return ruta_pkl

    @classmethod
    def cargar_partida_serializada(cls, codigo: str) -> PartidaJuego:
        ruta_pkl = os.path.join(cls.SAVES_DIR, f"{codigo.upper()}.pkl")
        if not os.path.exists(ruta_pkl):
            raise FileNotFoundError(f"No existe una partida guardada con código {codigo}.")
        with open(ruta_pkl, "rb") as f_pkl:
            return pickle.load(f_pkl)

    @classmethod
    def listar_partidas_guardadas(cls) -> list[dict]:
        cls.asegurar_directorios()
        guardadas = []
        for archivo in os.listdir(cls.SAVES_DIR):
            if archivo.endswith(".json"):
                with open(os.path.join(cls.SAVES_DIR, archivo), "r", encoding="utf-8") as f:
                    guardadas.append(json.load(f))
        return guardadas

    @classmethod
    def exportar_ranking_csv(cls, jugadores_data: list[dict]) -> str:
        cls.asegurar_directorios()
        nombre_archivo = f"ranking_navy_fighter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        ruta_csv = os.path.join(cls.OUTPUT_DIR, nombre_archivo)

        with open(ruta_csv, "w", newline="", encoding="utf-8") as f_csv:
            campos = ["id", "username", "partidas_jugadas", "victorias", "disparos_totales", "aciertos_totales", "precision"]
            writer = csv.DictWriter(f_csv, fieldnames=campos)
            writer.writeheader()
            for row in jugadores_data:
                writer.writerow(row)

        return ruta_csv