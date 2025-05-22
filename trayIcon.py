#!/usr/bin/env python3

# Importaciones básicas
import gi
import subprocess
import gettext
import os
import locale
import sched
import time
import datetime
import threading

# Módulo local para manejo de temas
import Theme as tema
import SunJob as sunjob

# Configuración de versiones GTK requeridas
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, GLib, AppIndicator3

class SystemTrayIcon:
    """Main class to handle the system tray icon and its menu"""
    is_day = True   
    automatic_theme = True  # Activado por defecto
    scheduler = sched.scheduler(time.time, time.sleep)
    current_event = None

    def __init__(self):
        self._setup_localization()    
        self._setup_indicator()  
        self._build_menu()
        # Programar primer evento al iniciar
        if self.automatic_theme:
            self._schedule_initial_event()

    def _setup_indicator(self):
        """Set the system tray indicator"""
        icondir = os.path.join(os.path.dirname(__file__), 'icons')
        icono = os.path.join(icondir, "day-and-night.png")
        self.indicator = AppIndicator3.Indicator.new(
            "tray-theme-icon",
            icono,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_icon_theme_path(icondir) 
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
    def _setup_localization(self):
        """Configure string localization"""
        locale_dir = os.path.join(os.path.dirname(__file__), 'locales')
        system_lang = locale.getlocale()[0]
        lang = system_lang.split("_")[0] if system_lang else "en"
        traducciones = gettext.translation(
            'traymessages', 
            localedir=locale_dir, 
            languages=[lang],
            fallback=True
        )
        traducciones.install()
            
    def _build_menu(self):
        """Build the context menu"""
        self.menu = Gtk.Menu()
        
        # Elementos del menú
        self.auto_theme_item = Gtk.MenuItem()
        self.menu_items = [
            (Gtk.MenuItem(label=_("Tema Diurno")), self.set_day_theme),
            (Gtk.MenuItem(label=_("Tema Nocturno")), self.set_night_theme),
            (Gtk.MenuItem(label=_("Guardar Tema Actual")), self.save_theme),
            (self.auto_theme_item, self.toggle_auto_theme),
            (Gtk.MenuItem(label=_("Salir")), Gtk.main_quit)
        ]
        
        # Configurar ítem de tema automático
        self._update_auto_theme_label()
        
        # Añadir elementos al menú
        for item, action in self.menu_items:
            item.connect("activate", action)
            self.menu.append(item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def _update_auto_theme_label(self):
        """Actualiza la etiqueta del botón automático"""
        label = _("Desactivar Tema Automático") if self.automatic_theme else _("Activar Tema Automático")
        self.auto_theme_item.set_label(label)

    # Métodos de acción #####################################################
    
    def set_day_theme(self, widget):
        """Switch to daytime theme"""
        self.is_day = True
        tema.load_theme("dia")
        subprocess.run(["notify-send", _("☀️ Tema diurno activado")])

    def set_night_theme(self, widget):
        """Switch to night theme"""
        self.is_day = False
        tema.load_theme("noche")
        subprocess.run(["notify-send", _("🌙 Tema nocturno activado")])

    def save_theme(self, widget):
        """Save current theme"""
        try:
            theme_type = "dia" if self.is_day else "noche"
            tema.save_theme(theme_type)
            subprocess.run(["notify-send", _("✅ Tema guardado: {}").format(_("Diurno") if self.is_day else _("Nocturno"))])
        except Exception as e:
            print(f"Error: {e}")
            subprocess.run(["notify-send", _("❌ Error guardando tema")])

    def toggle_auto_theme(self, widget):
        """Alterna el estado del tema automático"""
        self.automatic_theme = not self.automatic_theme
        self._update_auto_theme_label()
        
        if self.automatic_theme:
            self._schedule_initial_event()
            subprocess.run(["notify-send", _("🌗 Tema automático ACTIVADO")])
        else:
            self._cancel_scheduled_events()
            subprocess.run(["notify-send", _("🌓 Tema automático DESACTIVADO")])

    def _schedule_initial_event(self):
        """Programa el primer evento al iniciar"""
        now = datetime.datetime.now()
        sunrise = datetime.datetime.strptime(sunjob.get_sunrise_local(), "%H:%M").time()
        sunset = datetime.datetime.strptime(sunjob.get_sunset_local(), "%H:%M").time()
        
        if now.time() < sunrise:
            next_event = "sunrise"
        elif now.time() < sunset:
            next_event = "sunset"
        else:
            next_event = "sunrise"
        
        self._schedule_event(next_event)

    def _schedule_event(self, event_type):
        """Programa un evento y muestra notificación"""
        def switch_theme():
            if event_type == "sunset":
                self.set_night_theme(None)
                next_event = "sunrise"
            else:
                self.set_day_theme(None)
                next_event = "sunset"
            
            if self.automatic_theme:
                self._schedule_event(next_event)

        now = datetime.datetime.now()
        event_time_str = sunjob.get_sunset_local() if event_type == "sunset" else sunjob.get_sunrise_local()
        event_time = datetime.datetime.strptime(event_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )

        # Ajustar para mañana si ya pasó
        if event_time < now:
            event_time += datetime.timedelta(days=1)

        delay = (event_time - now).total_seconds()
        
        # Cancelar evento anterior si existe
        if self.current_event:
            self.scheduler.cancel(self.current_event)
        
        # Programar nuevo evento
        self.current_event = self.scheduler.enter(delay, 1, switch_theme, ())
        threading.Thread(target=self.scheduler.run, daemon=True).start()
        
        # Notificar hora programada
        formatted_time = event_time.strftime("%H:%M")
        subprocess.run([
            "notify-send",
            _("⏰ Cambio programado a {} a las {}").format(
                _("noche") if event_type == "sunset" else _("día"),
                formatted_time
            )
        ])

    def _cancel_scheduled_events(self):
        """Cancela todos los eventos programados"""
        for event in self.scheduler.queue:
            self.scheduler.cancel(event)
        self.current_event = None

if __name__ == "__main__":
    tema.create_directories()
    SystemTrayIcon()
    Gtk.main()