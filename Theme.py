#!/usr/bin/env python3
import os
import subprocess

# Configuración principal
home = os.path.expanduser("~")
main_folder = os.path.join(home, ".config/tray-theme")

def crear_directorios():
    subdirs = ["dia", "noche"]
    try:
        for subdir in subdirs:
            path = os.path.join(main_folder, subdir)
            os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Error creando directorios: {e}")

def guardar_tema(tema):
    configuraciones = [
        ("xsettings", "xsettings.conf"),
        ("xfwm4", "xfwm4.conf"),
        ("xfce4-desktop", "xfce4-desktop.conf"),
    ]
    tema_path = os.path.join(main_folder, tema)
    
    try:
        os.makedirs(tema_path, exist_ok=True)
        
        for config, filename in configuraciones:
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

def cargar_tema(tema):
    tema_path = os.path.join(main_folder, tema)
    
    if not os.path.exists(tema_path):
        print(f"❌ Tema '{tema}' no encontrado")
        return
    
    try:
        _cargar_config_generica(tema_path, "xsettings")
        _cargar_config_generica(tema_path, "xfwm4")
        _cargar_config_generica(tema_path, "xfce4-desktop")
        _recargar_escritorio()
        
    except Exception as e:
        print(f"Error cargando tema: {e}")

def _cargar_config_generica(tema_path, canal):
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
                tipo = _inferir_tipo(valor, prop)
                
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

def _inferir_tipo(valor, prop):
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

def _recargar_escritorio():
    """Recarga la configuración del escritorio"""
    print("\n🔄 Recargando escritorio...")
    try:
        subprocess.run(["xfdesktop", "--reload"])
        print("✅ Recarga completada")
    except Exception as e:
        print(f"Error recargando escritorio: {e}")

if __name__ == "__main__":
    if not os.path.exists(main_folder):
        crear_directorios()
    
    # Ejemplo de uso:
    # GuardarTema("dia")
    # CargarTema("noche")