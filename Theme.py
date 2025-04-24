#!/usr/bin/env python3
import os
import subprocess

# Configuración principal
HOME = os.path.expanduser("~")
MAIN_FOLDER = os.path.join(HOME, ".config/tray-theme")

def create_directories():
    if not os.path.exists(MAIN_FOLDER):
        subprocess.run (["notify-send", "No existen configuraciones por favor guarde los temas!!"])
        subdirs = ["dia", "noche"]
        try:
            for subdir in subdirs:
                path = os.path.join(MAIN_FOLDER, subdir)
                os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")

def save_theme(tema):
    configs = [
        ("xsettings", "xsettings.conf"),
        ("xfwm4", "xfwm4.conf"),
        ("xfce4-desktop", "xfce4-desktop.conf"),
    ]
    tema_path = os.path.join(MAIN_FOLDER, tema)
    
    try:
        os.makedirs(tema_path, exist_ok=True)
        
        for config, filename in configs:
            file_path = os.path.join(tema_path, filename)
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

def load_theme(tema):
    tema_path = os.path.join(MAIN_FOLDER, tema)
    
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

def _load_generic_config(tema_path, canal):
    """Carga configuración para cualquier canal"""
    archivo = os.path.join(tema_path, f"{canal}.conf")
    print(f"\nCARGANDO {canal.upper()} DESDE: {archivo}")
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return
    
    try:
        with open(archivo, "r") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                
                if ' = ' in linea:
                    prop, valor = linea.split(' = ', 1)
                else:
                    partes = linea.split(maxsplit=1)
                    if len(partes) < 2:
                        continue
                    prop, valor = partes
                
                valor = valor.strip('"\'')
                tipo = _infer_type(valor, prop)
                
                cmd = [
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

def _infer_type(valor, prop):
    """Infiere el tipo de dato con soporte para propiedades especiales"""
    valor = valor.strip('"\'').lower()
    tipo_especial = {
        '/gtk/xft-hinting': 'int',
        '/gtk/xft-antialias': 'int',
        '/gtk/font-name': 'string',
        '/net/theme-name': 'string'
    }
    
    if prop.lower() in tipo_especial:
        return tipo_especial[prop.lower()]
    
    if valor.startswith('[') and valor.endswith(']'):
        return 'array'
    if valor in ('true', 'false'):
        return 'bool'
    if valor.isdigit():
        return 'int'
    if valor.replace('.', '', 1).isdigit():
        return 'double'
    return 'string'

def _reload_desktop():
    """Recarga la configuración del escritorio"""
    print("\n🔄 Recargando escritorio...")
    try:
        subprocess.run(["xfdesktop", "--reload"])
        print("✅ Recarga completada")
    except Exception as e:
        print(f"Error recargando escritorio: {e}")
