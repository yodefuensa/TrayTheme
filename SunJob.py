#!/usr/bin/env python3
"""
SunJob module - Handles sunrise/sunset API calls and timezone conversions.
"""
import requests
from datetime import datetime, timezone, date, tzinfo
from typing import Tuple


def _get_lat_lon() -> Tuple[str, str]:
    """
    Get latitude and longitude from IP geolocation API.
    
    Returns:
        Tuple[str, str]: Latitude and longitude as strings.
    """
    data = requests.get('http://ip-api.com/line/?fields=lat,lon', timeout=10).text.strip().split('\n')
    return data[0], data[1]


def _get_sunrise_sunset_api_data(field_name: str) -> str:
    """
    Helper function to get data from the API sunrise-sunset.org.
    
    Args:
        field_name: Either 'sunrise' or 'sunset'
        
    Returns:
        str: The time in HH:MM (UTC) format or an error message.
    """
    lat, lon = _get_lat_lon()
    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0&tzid=UTC"
    response = requests.get(api_url, timeout=10)
    data = response.json()
    iso_format_time = data.get('results', {}).get(field_name)
    return iso_format_time[11:16]


def get_sunrise_UTC() -> str:
    """Get sunrise time in UTC format HH:MM."""
    return _get_sunrise_sunset_api_data('sunrise')


def get_sunset_UTC() -> str:
    """Get sunset time in UTC format HH:MM."""
    return _get_sunrise_sunset_api_data('sunset')


def get_sunrise_local() -> str:
    """Get sunrise time in local timezone HH:MM format."""
    utc_hhmm_str = get_sunrise_UTC()
    return convert_utc_hhmm_to_local_hhmm(utc_hhmm_str)


def get_sunset_local() -> str:
    """Get sunset time in local timezone HH:MM format."""
    utc_hhmm_str = get_sunset_UTC()
    return convert_utc_hhmm_to_local_hhmm(utc_hhmm_str)


def convert_utc_hhmm_to_local_hhmm(utc_hhmm_str: str) -> str:
    """
    Convert a time in UTC "HH:MM" format to local system time.
    
    This function takes the sunrise/sunset times returned by the API (in UTC)
    and converts them to the user's local timezone for accurate scheduling.
    
    Args:
        utc_hhmm_str: Time string in HH:MM format (UTC).
        
    Returns:
        str: Time converted to local timezone in HH:MM format, or error message.
    """
    # Validate input format
    if not isinstance(utc_hhmm_str, str) or len(utc_hhmm_str) != 5 or utc_hhmm_str[2] != ':':
        return f"UTC time not valid for conversion: {utc_hhmm_str}"
    
    try:
        # Parse UTC "HH:MM" time
        parsed_time = datetime.strptime(utc_hhmm_str, "%H:%M").time()
        
        # Combine with current date to create a datetime object (needed for timezone conversion)
        today_date = date.today()
        utc_datetime = datetime.combine(today_date, parsed_time, tzinfo=timezone.utc)
        # Get system's local timezone
        local_tz: tzinfo | None = datetime.now().astimezone().tzinfo
        
        # Convert UTC time to local timezone
        local_datetime = utc_datetime.astimezone(local_tz)
        
        return local_datetime.strftime("%H:%M")
        
    except ValueError:
        return f"Error: Invalid UTC time format '{utc_hhmm_str}'. Must be HH:MM."
    except Exception as e:
        return f"Error during time conversion: {e}"


