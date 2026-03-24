#!/usr/bin/env python3
"""
TrayIcon module - System tray icon for XFCE theme switching.
Handles UI and user interactions for theme management.
"""

# Importaciones básicas
import gi
import subprocess
import gettext
import os
import locale
import datetime
from typing import Optional, Callable, Any

# Módulos locales para manejo de temas
import Theme as tema
import SunJob as sunjob
from ThemeScheduler import ThemeScheduler
from Config import ConfigManager

# Configuración de versiones GTK requeridas
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, AppIndicator3


class SystemTrayIcon:
    """Main class to handle the system tray icon and its menu."""
    
    def __init__(self) -> None:
        """Initialize the system tray icon and theme scheduler."""
        self.config: ConfigManager = ConfigManager()
        self.is_day: bool = True
        self.automatic_theme: bool = self.config.get_automatic_theme()
        self.scheduler: ThemeScheduler = ThemeScheduler()
        
        self._setup_localization()
        self._setup_indicator()
        self._build_menu()
        
        # Schedule initial event if automatic theme is enabled
        if self.automatic_theme:
            self._start_automatic_theme()

    def _setup_indicator(self) -> None:
        """Set up the system tray indicator."""
        icondir: str = os.path.join(os.path.dirname(__file__), 'icons')
        icono: str = os.path.join(icondir, "day-and-night.png")
        self.indicator: AppIndicator3.Indicator = AppIndicator3.Indicator.new(
            "tray-theme-icon",
            icono,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_icon_theme_path(icondir)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Create menu object
        self.menu: Gtk.Menu = Gtk.Menu()
        self.indicator.set_menu(self.menu)
        
    def _setup_localization(self) -> None:
        """Configure string localization."""
        locale_dir: str = os.path.join(os.path.dirname(__file__), 'locales')
        system_lang: Optional[str] = locale.getlocale()[0]
        lang: str = system_lang.split("_")[0] if system_lang else "en"
        traducciones: gettext.GNUTranslations = gettext.translation(
            'traymessages',
            localedir=locale_dir,
            languages=[lang],
            fallback=True
        )
        traducciones.install()
            
    def _build_menu(self) -> None:
        """Build the context menu."""
        self._rebuild_menu()
    
    def _rebuild_menu(self) -> None:
        """Rebuild the context menu (called after state changes for auto-refresh)."""
        # Clear existing menu items
        for item in self.menu:
            self.menu.remove(item)
        
        # Recreate menu items
        self.auto_theme_item: Gtk.MenuItem = Gtk.MenuItem()
        self.next_event_item: Gtk.MenuItem = Gtk.MenuItem()
        
        menu_items: list[tuple[Gtk.MenuItem, Callable[[Any], None]]] = [
            (Gtk.MenuItem(label=_("☀️ Tema Diurno")), self.set_day_theme),
            (Gtk.MenuItem(label=_("🌙 Tema Nocturno")), self.set_night_theme),
            (Gtk.MenuItem(label=_("💾 Guardar Tema Actual")), self.save_theme),
            (Gtk.SeparatorMenuItem(), None),
            (self.auto_theme_item, self.toggle_auto_theme),
            (self.next_event_item, None),
            (Gtk.SeparatorMenuItem(), None),
            (Gtk.MenuItem(label=_("🚪 Salir")), Gtk.main_quit)
        ]
        
        # Update labels
        self._update_auto_theme_label()
        self._update_status_labels()
        
        # Add menu items
        for item, action in menu_items:
            if action is not None:
                item.connect("activate", action)
            self.menu.append(item)
        
        self.menu.show_all()

    def _update_auto_theme_label(self) -> None:
        """Update the automatic theme toggle menu item label."""
        label: str = (
            _("Desactivar Tema Automático") 
            if self.automatic_theme 
            else _("Activar Tema Automático")
        )
        self.auto_theme_item.set_label(label)
    
    def _update_status_labels(self) -> None:
        """Update status information labels in the menu."""
        # Update next event information (shows scheduled sunrise/sunset time)
        event_label, time_str = self.scheduler.get_next_event_info()
        if event_label and time_str:
            next_text = f"⏰ Próximo cambio: {event_label} a las {time_str}"
        else:
            next_text = "⏰ Sin eventos programados"
        self.next_event_item.set_label(next_text)
    
    def _refresh_menu_display(self) -> None:
        """Refresh menu display after state changes (for auto-update)."""
        self._rebuild_menu()

    # Action methods
    
    def set_day_theme(self, widget: Any) -> None:
        """Switch to daytime theme."""
        self.is_day = True
        tema.load_theme("dia")
        self.config.set_last_theme("dia")
        self._rebuild_menu()
        subprocess.run(["notify-send", _("☀️ Tema diurno activado")])
    
    def set_night_theme(self, widget: Any) -> None:
        """Switch to nighttime theme."""
        self.is_day = False
        tema.load_theme("noche")
        self.config.set_last_theme("noche")
        self._rebuild_menu()
        subprocess.run(["notify-send", _("🌙 Tema nocturno activado")])

    def save_theme(self, widget: Any) -> None:
        """Save current theme configuration."""
        try:
            theme_type: str = "dia" if self.is_day else "noche"
            tema.save_theme(theme_type)
            subprocess.run([
                "notify-send",
                _("✅ Tema guardado: {}").format(
                    _("Diurno") if self.is_day else _("Nocturno")
                )
            ])
        except Exception as e:
            print(f"Error: {e}")
            subprocess.run(["notify-send", _("❌ Error guardando tema")])

    def toggle_auto_theme(self, widget: Any) -> None:
        """Toggle automatic theme switching on/off."""
        self.automatic_theme = not self.automatic_theme
        self.config.set_automatic_theme(self.automatic_theme)
        
        if self.automatic_theme:
            self._start_automatic_theme()
            self._rebuild_menu()
            subprocess.run(["notify-send", _("🌗 Tema automático ACTIVADO")])
        else:
            self._stop_automatic_theme()
            self._rebuild_menu()
            subprocess.run(["notify-send", _("🌓 Tema automático DESACTIVADO")])

    def _start_automatic_theme(self) -> None:
        """Start automatic theme switching based on sunrise/sunset."""
        try:
            self.scheduler.schedule_initial_event(
                on_sunrise=lambda: self.set_day_theme(None),
                on_sunset=lambda: self.set_night_theme(None)
            )
            # Refresh menu to show scheduled times
            self._rebuild_menu()
        except Exception as e:
            print(f"Error starting automatic theme: {e}")
            subprocess.run([
                "notify-send",
                _("❌ Error al activar tema automático")
            ])

    def _stop_automatic_theme(self) -> None:
        """Stop automatic theme switching."""
        self.scheduler.cancel_all_events()


if __name__ == "__main__":
    tema.create_directories()
    SystemTrayIcon()
    Gtk.main()