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

class SystemTrayIcon:
    """Main class to handle the system tray icon and its menu"""
    
    def __init__(self):
        self._setup_localization()  # Configurar localización    
        self._setup_indicator()  
        self._build_menu()

    def _setup_indicator(self):
        """Set the system tray indicator"""
        icondir = os.path.join(os.path.dirname(__file__), 'icons')
        icono = os.path.join(icondir, "day-and-night.png")
        self.indicator = AppIndicator3.Indicator.new(
            "unique-tray-id",  # ID único para la aplicación
            icono,  # Ícono inicial
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_icon_theme_path(icondir) 
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
    def _setup_localization(self):
        """Configure string localization and translation"""
        locale_dir = os.path.join(os.path.dirname(__file__), 'locales')
        system_lang = locale.getlocale()[0] #Devuelve es_ES
        # Extraer el idioma del sistema (ej. 'es' de 'es_ES')
        # Si no se encuentra el idioma, se usa inglés como predeterminado
        lang = system_lang.split("_")[0] if system_lang else "en"  # Fallback a inglés
        traducciones = gettext.translation(
            'traymessages', 
            localedir=locale_dir, 
            languages=[lang],
            fallback=True  # Usa cadenas originales si no encuentra traducción
        )
        traducciones.install()

    def _build_menu(self):
        """Build the context menu with its elements and actions"""
        self.menu = Gtk.Menu()
        
        # Elements of the menu and their actions
        menu_items = [
            (_("Tema Diurno"), self.set_day_theme),
            (_("Tema Nocturno"), self.set_night_theme),
            (_("Guardar Tema Actual"), self.save_theme),
            (_("Salir"), Gtk.main_quit)
        ]
        
        # Create and add items to the menu
        for label, action in menu_items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", action)  # connect the action
            self.menu.append(item)
        
        self.menu.show_all()  # Show all menu items
        self.indicator.set_menu(self.menu)

    # Actions metods #####################################################
    
    def set_day_theme(self, widget):
        """Switch to daytime theme and update status"""
        global is_day
        tema.load_theme("dia")
        is_day = True

    def set_night_theme(self, widget):
        """Switch to night theme and update status"""
        global is_day
        tema.load_theme("noche")
        is_day = False

    def save_theme(self, widget):
        """Save the current theme and notify the user"""
        try:
            if is_day:
                tema.save_theme("dia")
                subprocess.run(["notify-send", _("☀️ Guardado tema")])
            else:
                tema.save_theme("noche")
                subprocess.run(["notify-send", _("🌙 Guardado tema")])
        except Exception as e:
            print(f"Error al guardar tema: {e}")
            subprocess.run(["notify-send", _("❌ Error guardando tema")])

if __name__ == "__main__":
    # Inicialización principal
    tema.create_directories()  # Asegurar que existen los directorios necesarios
    SystemTrayIcon()  # Crear instancia del ícono
    Gtk.main()  # Iniciar el bucle principal de GTK