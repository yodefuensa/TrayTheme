#!/usr/bin/env python3
"""
Theme module - Handles XFCE theme configuration saving and loading.
"""
import os
import subprocess
from typing import List, Tuple, Optional

# Configuración principal
HOME: str = os.path.expanduser("~")
MAIN_FOLDER: str = os.path.join(HOME, ".config/tray-theme")


def create_directories() -> None:
    """Create default theme directory structure if it doesn't exist."""
    if not os.path.exists(MAIN_FOLDER):
        subprocess.run(["notify-send", "No existen configuraciones por favor guarde los temas!!"])
        subdirs = ["dia", "noche"]
        try:
            for subdir in subdirs:
                path = os.path.join(MAIN_FOLDER, subdir)
                os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")


def save_theme(tema: str) -> None:
    """
    Save current XFCE configuration as a theme.
    
    Args:
        tema: Theme name ('dia' or 'noche').
    """
    configs: List[Tuple[str, str]] = [
        ("xsettings", "xsettings.conf"),
        ("xfwm4", "xfwm4.conf"),
        ("xfce4-desktop", "xfce4-desktop.conf"),
    ]
    tema_path: str = os.path.join(MAIN_FOLDER, tema)
    
    try:
        os.makedirs(tema_path, exist_ok=True)
        
        for config, filename in configs:
            file_path: str = os.path.join(tema_path, filename)
            print(f"\nGUARDANDO {config} PARA TEMA '{tema}' EN: {file_path}")
            
            with open(file_path, "w") as f:
                subprocess.run(
                    ["xfconf-query", "-c", config, "-lv"],
                    stdout=f,
                    check=True,
                    text=True
                )
            print("¡Éxito!")
                
    except Exception as e:
        print(f"Error guardando tema: {e}")

def load_theme(tema: str) -> None:
    """
    Load a previously saved theme configuration.
    
    Args:
        tema: Theme name ('dia' or 'noche').
    """
    tema_path: str = os.path.join(MAIN_FOLDER, tema)
    
    if not os.path.exists(tema_path):
        print(f"❌ Tema '{tema}' no encontrado")
        return
    
    try:
        _load_generic_config(tema_path, "xsettings")
        _load_generic_config(tema_path, "xfwm4")
        _load_generic_config(tema_path, "xfce4-desktop")
        _reload_desktop()
        
    except Exception as e:
        print(f"Error cargando tema: {e}")

def _load_generic_config(tema_path: str, canal: str) -> None:
    """
    Load configuration for any XFCE channel.
    
    Reads a .conf file and applies each setting via xfconf-query.
    This handles parsing of XFCE configuration files with proper type inference.
    
    Args:
        tema_path: Path to the theme directory.
        canal: XFCE channel name (e.g., 'xsettings', 'xfwm4').
    """
    archivo: str = os.path.join(tema_path, f"{canal}.conf")
    print(f"\nCARGANDO {canal.upper()} DESDE: {archivo}")
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return
    
    try:
        with open(archivo, "r") as f:
            for linea in f:
                linea = linea.strip()
                # Skip empty lines and comments
                if not linea or linea.startswith("#"):
                    continue
                
                # Parse key=value pairs (handles both ' = ' and space separators)
                if ' = ' in linea:
                    prop, valor = linea.split(' = ', 1)
                else:
                    partes = linea.split(maxsplit=1)
                    if len(partes) < 2:
                        continue
                    prop, valor = partes
                
                valor = valor.strip('"\'')
                # Infer data type for xfconf-query to apply correctly
                tipo: str = _infer_type(valor, prop)
                
                # Apply setting using xfconf-query
                cmd: List[str] = [
                    "xfconf-query", "-c", canal,
                    "-p", prop,
                    "-s", valor,
                    "-t", tipo,
                    "--create"
                ]
                subprocess.run(cmd, check=True)
                print(f"✓ {prop}")
                
    except Exception as e:
        print(f"Error cargando {canal}: {e}")

def _infer_type(valor: str, prop: str) -> str:
    """
    Infer the data type from value and property name.
    
    This is crucial because xfconf-query requires the correct type flag to apply
    settings properly. Some properties have known types (like font names), while
    others are inferred from their values.
    
    Args:
        valor: The configuration value.
        prop: The property name.
        
    Returns:
        str: Inferred type ('array', 'bool', 'int', 'double', 'string').
    """
    valor = valor.strip('"\'').lower()
    # Special cases: some properties always have specific types
    tipo_especial: dict[str, str] = {
        '/gtk/xft-hinting': 'int',
        '/gtk/xft-antialias': 'int',
        '/gtk/font-name': 'string',
        '/net/theme-name': 'string'
    }
    
    if prop.lower() in tipo_especial:
        return tipo_especial[prop.lower()]
    
    # Infer from value content
    if valor.startswith('[') and valor.endswith(']'):
        return 'array'
    if valor in ('true', 'false'):
        return 'bool'
    if valor.isdigit():
        return 'int'
    if valor.replace('.', '', 1).isdigit():
        return 'double'
    return 'string'

def _reload_desktop() -> None:
    """Reload desktop configuration after theme changes."""
    print("\n🔄 Recargando escritorio...")
    try:
        subprocess.run(["xfdesktop", "--reload"])
        print("✅ Recarga completada")
    except Exception as e:
        print(f"Error recargando escritorio: {e}")
