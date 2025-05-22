#!/usr/bin/env python3
import requests
from datetime import datetime, timezone, date # Importaciones necesarias para la fecha y hora

def _get_lan_lon():
    data = requests.get('http://ip-api.com/line/?fields=lat,lon', timeout=10).text.strip().split('\n')
    return data[0], data[1]


def _get_sunrise_sunset_api_data(field_name):
    lat, lon = _get_lan_lon ()
    """
    Función auxiliar para obtener datos de la API sunrise-sunset.org.
    Retorna la hora en formato HH:MM (UTC) o un mensaje de error.
    """
    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0&tzid=UTC"
    response = requests.get(api_url, timeout=10)
    data = response.json()
    iso_format_time = data.get('results', {}).get(field_name)
    return iso_format_time[11:16]

def get_sunrise_UTC():
    return _get_sunrise_sunset_api_data('sunrise')

def get_sunset_UTC():
    return _get_sunrise_sunset_api_data('sunset')

def get_sunrise_local():
    utc_hhmm_str = get_sunrise_UTC()
    return convert_utc_hhmm_to_local_hhmm(utc_hhmm_str)

def get_sunset_local():
    utc_hhmm_str = get_sunset_UTC()
    return convert_utc_hhmm_to_local_hhmm(utc_hhmm_str)

def convert_utc_hhmm_to_local_hhmm(utc_hhmm_str):
    """
    Convierte una hora en formato "HH:MM" de UTC a la hora local del sistema.
    Retorna la hora local en formato "HH:MM" o un mensaje de error.
    """
    if not isinstance(utc_hhmm_str, str) or len(utc_hhmm_str) != 5 or utc_hhmm_str[2] != ':':
        # Es un mensaje de error de una función anterior, o formato incorrecto.
        return f"Hora UTC no válida para conversión: {utc_hhmm_str}"

    try:
        # Parsea la hora UTC "HH:MM"
        parsed_time = datetime.strptime(utc_hhmm_str, "%H:%M").time()
        
        # Combina con la fecha actual para crear un objeto datetime
        # La API sunrise-sunset.org devuelve los tiempos para el día actual (en UTC)
        # si no se especifica una fecha en la petición.
        today_date = date.today()
        utc_datetime = datetime.combine(today_date, parsed_time, tzinfo=timezone.utc)
        local_tz = datetime.now().astimezone().tzinfo
        
        # Convierte a la zona horaria local
        local_datetime = utc_datetime.astimezone(local_tz)
        
        return local_datetime.strftime("%H:%M")
        
    except ValueError:
        return f"Error: Formato de hora UTC inválido '{utc_hhmm_str}'. Debe ser HH:MM."
    except Exception as e:
        return f"Error durante la conversión de hora: {e}"


