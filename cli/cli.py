import typer
import requests
from datetime import datetime

app = typer.Typer()

API_URL = "http://localhost:8001"


@app.command()
def health():
    """Verificar si el servidor está corriendo"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("Servidor activo")
        else:
            print("Servidor no responde correctamente")
    except requests.exceptions.ConnectionError:
        print("No se puede conectar al servidor")


@app.command()
def eventos():
    """Listar todos los eventos del calendario"""
    try:
        response = requests.get(f"{API_URL}/events")
        if response.status_code == 200:
            eventos = response.json()
            if not eventos:
                print("No hay eventos")
                return
            
            for evento in eventos:
                print(f"\nTitulo: {evento['title']}")
                print(f"Inicio: {evento['start']}")
                print(f"Fin: {evento['end']}")
        else:
            print("Error al obtener eventos")
    except requests.exceptions.ConnectionError:
        print("No se puede conectar al servidor")
    except Exception as e:
        print(f"Error: {str(e)}")


@app.command()
def disponibilidad(dias: int = typer.Option(None, help="Cantidad de dias a consultar")):
    """Ver horarios disponibles"""
    try:
        if dias:
            response = requests.get(f"{API_URL}/availability?days={dias}")
        else:
            response = requests.get(f"{API_URL}/availability")
        
        if response.status_code == 200:
            slots = response.json()
            if not slots:
                print("No hay horarios disponibles")
                return
            
            print(f"Horarios disponibles: {len(slots)} slots")
            for i, slot in enumerate(slots[:10], 1):
                inicio = slot['start'].split('T')[1][:5]
                fecha = slot['start'].split('T')[0]
                print(f"{i}. {fecha} - {inicio}")
            
            if len(slots) > 10:
                print(f"... y {len(slots) - 10} mas")
        else:
            print("Error al obtener disponibilidad")
    except requests.exceptions.ConnectionError:
        print("No se puede conectar al servidor")
    except Exception as e:
        print(f"Error: {str(e)}")


@app.command()
def agendar(
    titulo: str = typer.Argument(..., help="Titulo del evento"),
    inicio: str = typer.Argument(..., help="Inicio (YYYY-MM-DD HH:MM)"),
    fin: str = typer.Argument(..., help="Fin (YYYY-MM-DD HH:MM)")
):
    """Crear un evento en el calendario"""
    try:
        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d %H:%M").isoformat()
        fin_dt = datetime.strptime(fin, "%Y-%m-%d %H:%M").isoformat()
        
        data = {
            "title": titulo,
            "start": inicio_dt,
            "end": fin_dt
        }
        
        response = requests.post(f"{API_URL}/schedule", json=data)
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"Evento creado: {resultado['event_id']}")
        else:
            error = response.json()
            print(f"Error: {error.get('detail', 'Error desconocido')}")
    except ValueError:
        print("Formato de fecha invalido. Usa: YYYY-MM-DD HH:MM")
    except requests.exceptions.ConnectionError:
        print("No se puede conectar al servidor")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    app()