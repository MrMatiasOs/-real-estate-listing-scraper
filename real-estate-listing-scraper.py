import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pytz

def main():
    url = input("Introduce el enlace de la publicación: ")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    date_patterns = [
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}',  # ISO 8601 con zona horaria
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        # Añadir más patrones según sea necesario
    ]

    fecha_publicacion = None

    for pattern in date_patterns:
        match = re.search(pattern, response.text)
        if match:
            fecha_publicacion_str = match.group()
            try:
                if 'T' in fecha_publicacion_str:  # Si es ISO 8601
                    fecha_publicacion = datetime.strptime(fecha_publicacion_str, "%Y-%m-%dT%H:%M:%S%z")
                elif '/' in fecha_publicacion_str:  # Si es DD/MM/YYYY
                    fecha_publicacion = datetime.strptime(fecha_publicacion_str, "%d/%m/%Y")
                else:  # Asume YYYY-MM-DD
                    fecha_publicacion = datetime.strptime(fecha_publicacion_str, "%Y-%m-%d")
                break  # Sal del bucle una vez encontrada la fecha
            except ValueError:
                print("Formato de fecha no reconocido:", fecha_publicacion_str)
                continue
    
    if fecha_publicacion is not None:
        # Obtener la fecha actual con zona horaria
        fecha_actual = datetime.now(pytz.timezone('UTC'))  # Asumiendo que quieres UTC, ajusta según necesites

        # Calcular la diferencia entre las dos fechas
        diferencia = fecha_actual - fecha_publicacion

        # Convertir la diferencia a días
        dias_en_mercado = diferencia.days

        print(f"Fecha de publicación: {fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Días en el mercado: {dias_en_mercado}")
    else:
        print("No se encontró una fecha que coincida con los patrones dados.")

if __name__ == "__main__":
    main()