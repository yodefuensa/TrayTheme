# Tray Theme Switcher para XFCE

Un icono de bandeja para cambiar rápidamente entre temas diurnos/nocturnos en XFCE, con capacidad de guardar configuraciones personalizadas.

## Características
- Cambio rápido entre dos temas preconfigurados
- Guardado de la configuración actual del tema
- Notificaciones visuales al guardar/cambiar temas


## Dependencias
- Entorno de escritorio XFCE
- Paquetes necesarios:
python3-gi libappindicator3-dev xfconf libnotify-bin


## Instalación
1.Clona o descarga los archivos del proyecto:
git clone https://github.com/tu-usuario/tray-theme-switcher.git
cd tray-theme-switcher

~~2.Crea los directorios de configuración:~~ 
~~mkdir -p ~/.config/tray-theme/{dia,noche}~~
Es automatico al correr por primera vez el programa.

3.Haz ejecutables los scripts:
chmod +x Theme.py trayIcon.py

4.Ejecuta el icono de bandeja:
./trayIcon.py


Ah creditos a https://github.com/liamsgotgenes/xfce4-theme-switcher
que es de donde he sacado la gestión de los configs, y a DeepSeek, DeepSeek ha ayudado mucho

y el icono de la bandeja:
<a href="https://www.flaticon.com/free-icons/sun" title="sun icons">Sun icons created by xnimrodx - Flaticon</a>


![sig el gif no va](https://github.com/yodefuensa/TrayTheme/blob/main/doc_2025-04-07_18-43-06.gif)