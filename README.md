# Scheduler

Sistema de agendamiento con Google Calendar.

## Requisitos

- Python 3.12.7
- Poetry
- Cuenta de Google con acceso al calendario

## Instalación

Clonar el repositorio:

```bash
git clone <repo>
cd project scheduling automation
```

Instalar dependencias:

```bash
poetry install
```

Configurar Google Calendar:

1. Ir a https://console.cloud.google.com
2. Crear un proyecto nuevo
3. Habilitar Google Calendar API
4. Descargar credenciales OAuth (tipo Desktop)
5. Guardar en la raíz del proyecto como `client_secret.json`

## Uso

### API

Iniciar servidor:

```bash
poetry run uvicorn app.main:app --reload --port 8001
```

Endpoints disponibles:

- `GET /health` - Estado del servidor
- `GET /events` - Listar eventos
- `GET /availability` - Ver horarios libres (parámetro opcional `days`)
- `POST /schedule` - Crear un evento

### CLI

Verificar servidor:

```bash
poetry run scheduler health
```

Listar eventos:

```bash
poetry run scheduler eventos
```

Ver disponibilidad:

```bash
poetry run scheduler disponibilidad
poetry run scheduler disponibilidad --dias 7
```

Agendar evento:

```bash
poetry run scheduler agendar "Titulo" "2026-03-28 10:00" "2026-03-28 11:00"
```

## Configuración

Zona horaria: America/Bogota (Colombia)
Horario laboral: 9:00 AM - 5:00 PM
Descanso: 12:00 PM - 1:00 PM (almuerzo)

## Estructura

```
app/
├── api/
│   └── routes.py         # Endpoints
├── services/
│   ├── availability_service.py
│   ├── booking_service.py
│   └── calendar_service.py
├── models/
│   ├── event.py
│   └── schedule_request.py
├── clients/
│   └── google_calendar_client.py
├── core/
│   ├── config.py
│   └── logging.py
└── main.py

cli/
└── cli.py                # Comandos de línea de comandos
```