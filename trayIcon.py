#!/usr/bin/env python3
import gi
import subprocess
import gettext
import os
import locale
import Theme as tema


gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, GLib, AppIndicator3

is_day = True
localedir = os.path.join(os.path.dirname(__file__), 'locales')
system_lang = locale.getlocale()[0]
lang = system_lang.split("_")[0]
#lang= "en"
#lang= "pt"

traducciones = gettext.translation(
    'traymessages', 
    localedir=localedir, 
    languages=[lang],
    fallback=True  # Si no encuentra el idioma, usa cadenas originales
)
traducciones.install()


class SystemTrayIcon:
    def __init__(self):
        # Crea el indicador de la aplicación
        self.indicator = AppIndicator3.Indicator.new(
            "unique-tray-id",  # ID único
            "preferences-desktop-theme",  # Icono inicial
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Crea el menú contextual
        self.menu = Gtk.Menu()
        
        day_item = Gtk.MenuItem(label=_("Tema Diurno"))
        day_item.connect("activate", self.set_day_theme)
        self.menu.append(day_item)
        
        night_item = Gtk.MenuItem(label=_("Tema Nocturno"))
        night_item.connect("activate", self.set_night_theme)
        self.menu.append(night_item)

        save_item = Gtk.MenuItem(label=_("Guardar Tema Actual"))
        save_item.connect("activate", self.save_theme)
        self.menu.append(save_item)    
        
        exit_item = Gtk.MenuItem(label=_("Salir"))
        exit_item.connect("activate", Gtk.main_quit)
        self.menu.append(exit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)


    def set_day_theme(self, widget):
        global is_day
        tema.cargar_tema("dia")
        is_day = True
        print(is_day)


    def set_night_theme(self, widget):
        global is_day
        tema.cargar_tema("noche")
        is_day = False
        print(is_day)

    def save_theme(self, widget):
        if is_day:
            tema.guardar_tema("dia")
            subprocess.run(["notify-send",_("☀️ Guardado tema")])
        else:
            tema.guardar_tema("noche")
            subprocess.run (["notify-send",_("🌙 Guardado tema")])


if __name__ == "__main__":
    tema.crear_directorios()
    SystemTrayIcon()
    Gtk.main()