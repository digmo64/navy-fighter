import queue
import threading
import time
from app.models.file_manager import FileManager


class MonitorSalasThread(threading.Thread):
    def __init__(self, game_service, intervalo_segundos: int = 5, timeout_turno: int = 180):
        super().__init__(daemon=True, name="MonitorSalasThread")
        self.game_service = game_service
        self.intervalo = intervalo_segundos
        self.timeout_turno = timeout_turno
        self._activo = True

    def run(self) -> None:
        while self._activo:
            time.sleep(self.intervalo)
            self.game_service.verificar_inactividad_salas(self.timeout_turno)


class ExportadorCSVWorker(threading.Thread):
    def __init__(self, cola_tareas: queue.Queue):
        super().__init__(daemon=True, name="ExportadorCSVWorker")
        self.cola = cola_tareas
        self.ultimo_reporte: str | None = None

    def run(self) -> None:
        while True:
            tarea = self.cola.get()
            try:
                if tarea["tipo"] == "EXPORTAR_RANKING":
                    ruta = FileManager.exportar_ranking_csv(tarea["datos"])
                    self.ultimo_reporte = ruta
            finally:
                self.cola.task_done()