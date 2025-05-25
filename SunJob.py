#!/usr/bin/env python3
import requests
from datetime import datetime, timezone, date # Importaciones necesarias para la fecha y hora

def _get_lat_lon():
    data = requests.get('http://ip-api.com/line/?fields=lat,lon', timeout=10).text.strip().split('\n')
    return data[0], data[1]


def _get_sunrise_sunset_api_data(field_name):
    lat, lon = _get_lat_lon ()
    """
    Helper function to get data from the API sunrise-sunset.org. 
    Returns the time in HH:MM (UTC) format or an error message.
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
    Converts a time in UTC "HH:MM" format to local system time.    
    """
    if not isinstance(utc_hhmm_str, str) or len(utc_hhmm_str) != 5 or utc_hhmm_str[2] != ':':
        # Error message from a previous function, or incorrect formatting. //Check if the API response has changed
        return f"UTC time not valid for conversion: {utc_hhmm_str}"
    try:
        # Parse UTC "HH:MM" time
        parsed_time = datetime.strptime(utc_hhmm_str, "%H:%M").time()
        
        # Combine with current date to create a datetime object
        today_date = date.today()
        utc_datetime = datetime.combine(today_date, parsed_time, tzinfo=timezone.utc)
        local_tz = datetime.now().astimezone().tzinfo
        
        # Convert to local timezone
        local_datetime = utc_datetime.astimezone(local_tz)
        
        return local_datetime.strftime("%H:%M")
        
    except ValueError:
        return f"Error: Invalid UTC time format '{utc_hhmm_str}'. Must be HH:MM."
    except Exception as e:
        return f"Error during time conversion: {e}"


