# Navy Fighter

Aplicación web multijugador de estrategia naval por turnos desarrollada en Python y Flask. Permite crear salas en red local o a través de internet, gestionar perfiles de comandantes y plantillas de flota, guardar y reanudar partidas mediante serialización, y exportar estadísticas de rendimiento.

---

## Problema

Las implementaciones básicas de juegos de estrategia por turnos suelen operar únicamente en memoria local, sin arquitectura modular, sin soporte multijugador en red y sin persistencia de datos. Esto impide que dos jugadores compitan desde dispositivos distintos, reanuden partidas interrumpidas, personalicen configuraciones de flota o conserven un historial verificable de sus estadísticas.

## Objetivo General

Desarrollar una aplicación web multijugador en Python con el framework Flask que permita gestionar salas de batalla naval por turnos en red local o internet, incorporando persistencia relacional, serialización de estados de juego, procesamiento concurrente en segundo plano y una arquitectura modular basada en programación orientada a objetos y patrones de diseño.

---

## Funcionalidades Principales

* **Multijugador por turnos (LAN e Internet):** Creación de salas mediante códigos únicos de 4 caracteres y sincronización en tiempo real entre dos navegadores.
* **Despliegue táctico de flota:** Posicionamiento manual (horizontal o vertical) o automático de embarcaciones con validación de límites y colisiones.
* **Gestión CRUD completa:** Creación, consulta, edición y eliminación de perfiles de jugadores y plantillas de flota personalizadas almacenadas en SQLite.
* **Persistencia y serialización:** Registro de partidas y movimientos en base de datos relacional, además de guardado y reanudación de duelos en curso mediante archivos `.pkl` (Pickle) y `.json`.
* **Procesamiento concurrente:** Hilos en segundo plano (`threading` y `queue`) encargados de monitorear tiempos de inactividad en salas activas y exportar rankings a `.csv` sin bloquear la interfaz web.
* **Ranking y métricas:** Cálculo automático de partidas jugadas, victorias y porcentaje de precisión por jugador.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Framework Web:** Flask 3.0.3
* **ORM y Base de Datos:** SQLAlchemy 2.0.36 + SQLite
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API) y plantillas Jinja2
* **Concurrencia y Serialización:** Módulos estándar `threading`, `queue`, `pickle`, `json` y `csv`
* **Pruebas:** `unittest`

---

## Estructura General del Repositorio

```text
navy-fighter/
├── app/
│   ├── __init__.py              # Fábrica de la aplicación Flask
│   ├── domain/
│   │   ├── barcos.py            # Clases de embarcaciones, herencia y Patrón Factory
│   │   ├── tablero.py           # Lógica de cuadrícula, validaciones y disparos
│   │   ├── estados.py           # Patrón State (Esperando, Despliegue, En Curso, Finalizado)
│   │   └── partida.py           # Entidad principal de la sala multijugador
│   ├── persistence/
│   │   ├── database.py          # Configuración de motor y sesión SQLAlchemy
│   │   ├── models.py            # Modelos relacionales (Jugador, PlantillaFlota, Partida, Movimiento)
│   │   ├── repositories.py      # Patrón Repository para consultas CRUD
│   │   └── file_manager.py      # Lectura JSON, serialización Pickle y exportación CSV
│   ├── services/
│   │   ├── concurrency.py       # Hilos de monitoreo de salas y exportación asíncrona CSV
│   │   └── game_service.py      # Orquestación de reglas de negocio y salas activas
│   ├── interface/
│   │   └── routes.py            # Endpoints HTTP/JSON y vistas web
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html           # Lobby, ranking y administración CRUD
│   │   └── sala.html            # Interfaz de combate multijugador
│   └── static/
│       ├── css/style.css
│       └── js/game.js           # Sincronización asíncrona con el servidor
├── data/
│   ├── input/
│   │   └── flotas_default.json  # Plantillas base de flotas
│   ├── saves/                   # Partidas guardadas (.pkl y .json)
│   └── output/                  # Reportes de ranking exportados (.csv)
├── documentation/
│   ├── evidence/                # Capturas de pantalla y evidencias técnicas
│   └── project_report.pdf       # Informe académico y técnico del proyecto
├── tests/
│   ├── __init__.py
│   └── test_juego.py            # Pruebas unitarias del dominio y flujo de partida
├── main.py                      # Punto de entrada del servidor
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Documentación principal del repositorio
