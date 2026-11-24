import unittest
from app.domain.barcos import FlotaFactory
from app.domain.partida import PartidaJuego


class TestNavyFighter(unittest.TestCase):
    def test_factory_y_herencia(self):
        barco = FlotaFactory.crear_barco("portaaviones")
        self.assertEqual(barco.tamano, 4)
        self.assertEqual(barco.bono_hundimiento(), 50)

    def test_flujo_completo_partida(self):
        config = [{"tipo": "destructor", "cantidad": 1}]
        partida = PartidaJuego("TEST", "Prueba", 5, config)
        partida.registrar_jugador(1, "Alan")
        partida.unirse(2, "Diego")
        self.assertEqual(partida.estado.nombre, "DESPLIEGUE")

        ub1 = [{"fila": 0, "col": 0, "orientacion": "H"}]
        ub2 = [{"fila": 1, "col": 1, "orientacion": "H"}]
        partida.desplegar(1, ub1)
        partida.desplegar(2, ub2)
        self.assertEqual(partida.estado.nombre, "EN_CURSO")

        r1 = partida.disparar(1, 1, 1)
        self.assertEqual(r1["resultado"], "IMPACTO")
        partida.disparar(2, 4, 4)
        r2 = partida.disparar(1, 1, 2)
        self.assertEqual(r2["resultado"], "HUNDIDO")
        self.assertEqual(partida.estado.nombre, "FINALIZADO")
        self.assertEqual(partida.ganador_id, 1)


if __name__ == "__main__":
    unittest.main()