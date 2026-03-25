import typer
import requests

app = typer.Typer()

API_URL = "http://localhost:8001"


@app.command()
def health():
    """
    Check if API is running
    """
    response = requests.get(f"{API_URL}/health")
    print(response.json())


if __name__ == "__main__":
    app()