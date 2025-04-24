
# Tray Theme Switcher para XFCE

A tray icon to quickly switch between day/night themes in XFCE, with the ability to save custom configurations.
Features

## Features
    Quick switching between two preconfigured themes
    Saving the current theme configuration
    Visual notifications when saving/switching themes

## Dependencies

    XFCE desktop environment
    Required packages: python3-gi libappindicator3-dev xfconf libnotify-bin

## Installation

1.Clone or download the project files: 
git clone https://github.com/tu-usuario/tray-theme-switcher.git 
cd tray-theme-switcher

~~2. Create the configuration directories:~~
~~mkdir -p ~/.config/tray-theme/{day,night}~~
This is automatic when running the program for the first time.

3.Make the scripts executable:
chmod +x Theme.py trayIcon.py

4.Run the tray icon:
./trayIcon.py

Ah, credits to https://github.com/liamsgotgenes/xfce4-theme-switcher
which is where I got the configuration management from, and to DeepSeek, DeepSeek helped a lot.

and the tray icon:
<a href="https://www.flaticon.com/free-icons/sun" title="sun icons">Sun icons created by xnimrodx - Flaticon</a>

![](https://github.com/yodefuensa/TrayTheme/blob/main/doc_2025-04-07_18-43-06.gif)