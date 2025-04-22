#!/usr/bin/env python3

# Importaciones básicas
import gi
import subprocess
import gettext
import os
import locale

# Módulo local para manejo de temas
import Theme as tema

# Configuración de versiones GTK requeridas
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, GLib, AppIndicator3

# Estado global del tema (podría encapsularse en la clase)
is_day = True

# Configuración de internacionalización
localedir = os.path.join(os.path.dirname(__file__), 'locales')
system_lang = locale.getlocale()[0]
lang = system_lang.split("_")[0] if system_lang else "en"  # Fallback a inglés

# Cargar traducciones
traducciones = gettext.translation(
    'traymessages', 
    localedir=localedir, 
    languages=[lang],
    fallback=True  # Usa cadenas originales si no encuentra traducción
)
traducciones.install()

class SystemTrayIcon:
    """Clase principal para manejar el ícono de la bandeja del sistema y su menú"""
    
    def __init__(self):
        # Configurar el indicador de la bandeja
        icondir = os.path.join(os.path.dirname(__file__), 'icons')
        icono = os.path.join(icondir, "day-and-night.png")
        
        self.indicator = AppIndicator3.Indicator.new(
            "unique-tray-id",  # ID único para la aplicación
            icono,  # Ícono inicial
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_icon_theme_path(icondir)  # Mover esta línea aquí
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.build_menu()
        
    def build_menu(self):
        """Construye el menú contextual con sus elementos y acciones"""
        self.menu = Gtk.Menu()
        
        # Elementos del menú: (Etiqueta traducible, Acción)
        menu_items = [
            (_("Tema Diurno"), self.set_day_theme),
            (_("Tema Nocturno"), self.set_night_theme),
            (_("Guardar Tema Actual"), self.save_theme),
            (_("Salir"), Gtk.main_quit)
        ]
        
        # Crear y añadir elementos al menú
        for label, action in menu_items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", action)  # Conectar evento de clic
            self.menu.append(item)
        
        self.menu.show_all()  # Mostrar todos los elementos
        self.indicator.set_menu(self.menu)

    # Métodos de acciones #####################################################
    
    def set_day_theme(self, widget):
        """Cambia al tema diurno y actualiza el estado"""
        global is_day
        tema.cargar_tema("dia")
        is_day = True
        # print(is_day)  # Mejor eliminar en producción

    def set_night_theme(self, widget):
        """Cambia al tema nocturno y actualiza el estado"""
        global is_day
        tema.cargar_tema("noche")
        is_day = False
        # print(is_day)  # Mejor eliminar en producción

    def save_theme(self, widget):
        """Guarda el tema actual y muestra notificación"""
        try:
            if is_day:
                tema.guardar_tema("dia")
                subprocess.run(["notify-send", _("☀️ Guardado tema")])
            else:
                tema.guardar_tema("noche")
                subprocess.run(["notify-send", _("🌙 Guardado tema")])
        except Exception as e:
            print(f"Error al guardar tema: {e}")
            subprocess.run(["notify-send", _("❌ Error guardando tema")])

if __name__ == "__main__":
    # Inicialización principal
    tema.crear_directorios()  # Asegurar que existen los directorios necesarios
    SystemTrayIcon()  # Crear instancia del ícono
    Gtk.main()  # Iniciar el bucle principal de GTK