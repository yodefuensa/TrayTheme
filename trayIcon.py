#!/usr/bin/env python3
import gi
import subprocess
import Theme as tema

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, GLib, AppIndicator3

is_day = True

class SystemTrayIcon:
    def __init__(self):
        # Crea el indicador de la aplicación
        self.indicator = AppIndicator3.Indicator.new(
            "unique-tray-id",  # ID único
            "preferences-desktop-theme",  # Icono inicial
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Configuración 
        self.config = {
            "day_theme": "Adwaita",
            "night_theme": "Adwaita-dark",
        }

        # Crea el menú contextual
        self.menu = Gtk.Menu()
        
        day_item = Gtk.MenuItem(label="Tema Diurno")
        day_item.connect("activate", self.set_day_theme)
        self.menu.append(day_item)
        
        night_item = Gtk.MenuItem(label="Tema Nocturno")
        night_item.connect("activate", self.set_night_theme)
        self.menu.append(night_item)

        save_item = Gtk.MenuItem(label="Guardar Tema Actual")
        save_item.connect("activate", self.save_theme)
        self.menu.append(save_item)    
        
        exit_item = Gtk.MenuItem(label="Salir")
        exit_item.connect("activate", Gtk.main_quit)
        self.menu.append(exit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        


    def on_right_click(self, icon, button, time):
        menu = Gtk.Menu()

        # Opciones del menú
        day_item = Gtk.MenuItem(label="Tema Diurno")
        day_item.connect("activate", self.set_day_theme)
        menu.append(day_item)

        night_item = Gtk.MenuItem(label="Tema Nocturno")
        night_item.connect("activate", self.set_night_theme)
        menu.append(night_item)

        save_item = Gtk.MenuItem(label="Guardar tema")
        save_item.connect("activate", self.save_item)
        menu.append(save_item)

        exit_item = Gtk.MenuItem(label="Salir")
        exit_item.connect("activate", Gtk.main_quit)
        menu.append(exit_item)

        menu.show_all()
        menu.popup(None, None, None, self.tray_icon, button, time)


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
            subprocess.run(["notify-send", "☀️ Guardado tema"])
        else:
            tema.guardar_tema("noche")
            subprocess.run (["notify-send", "🌙 Guardado tema"])


if __name__ == "__main__":
    SystemTrayIcon()
    Gtk.main()