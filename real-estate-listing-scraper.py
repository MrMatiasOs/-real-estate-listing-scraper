import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pytz

def find_date_in_html(html_content):
    # Define more comprehensive date patterns
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}',  # ISO 8601 with timezone
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
        r'\d{2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}',  # DD Mon YYYY
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',  # Mon DD, YYYY
    ]

    for pattern in date_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            date_str = match.group()
            # Try parsing with different formats
            formats = [
                "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with timezone
                "%Y-%m-%d",  # YYYY-MM-DD
                "%d/%m/%Y",  # DD/MM/YYYY
                "%d.%m.%Y",  # DD.MM.YYYY
                "%d %b %Y",  # DD Mon YYYY
                "%b %d, %Y"  # Mon DD, YYYY
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
    return None
    

def main():
    url = input("Introduce el enlace de la publicación: ")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"Error al obtener la página: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # First, look for date in meta tags
    meta_date = soup.find('meta', attrs={'property': 'article:published_time'})
    if meta_date and 'content' in meta_date.attrs:
        fecha_publicacion = datetime.fromisoformat(meta_date['content'])
    else:
        # If not in meta, search the entire HTML content
        fecha_publicacion = find_date_in_html(response.text)

    if fecha_publicacion is not None:
        # Ensure fecha_publicacion has timezone info
        if not fecha_publicacion.tzinfo:  # If the datetime is naive
            fecha_publicacion = pytz.utc.localize(fecha_publicacion)
        
        # Get current date with timezone
        fecha_actual = datetime.now(pytz.timezone('UTC'))

        # Calculate difference between dates
        diferencia = fecha_actual - fecha_publicacion

        # Convert difference to days
        dias_en_mercado = diferencia.days

        print(f"Fecha de publicación: {fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Días en el mercado: {dias_en_mercado}")
    else:
        print("No se encontró una fecha de publicación que coincida con los patrones dados.")
        # Optionally, print parts of the HTML where the date might be expected for debugging:
        possible_date_locations = soup.find_all(['time', 'span', 'p'], string=re.compile(r'\d+'))
        if possible_date_locations:
            print("Posibles ubicaciones de la fecha en el HTML:")
            for loc in possible_date_locations[:5]:  # Limit to first 5 to avoid cluttering output
                print(loc.prettify())

                

if __name__ == "__main__":
    main()