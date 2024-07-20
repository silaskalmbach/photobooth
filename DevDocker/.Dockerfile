# FROM balenalib/raspberrypi4-64-ubuntu:focal-run
# FROM balenalib/raspberrypi4-64-ubuntu:focal-run
FROM ubuntu:20.04
# FROM ubuntu:focal
# Infos zu den balenalib images und dem Etrypoint um dynamisch die USB-Geräte zu erkennen
# https://github.com/balena-io-library/base-images/blob/28844485a91b1408ffc550faa3b59e64809bc453/scripts/assets/entry.sh#L64-L68

# https://github.com/balena-io-examples/jetson-nano-x11/blob/master/nano_32_4/Dockerfile.template
# https://linuxhint.com/what-is-ld-library-path/


# SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND noninteractive

# Sprachen einstellen
RUN apt-get update -y

# SK eingene Installation Ubuntu
# RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
# RUN apt-get install -y apt-utils 
RUN apt-get install -y neovim ranger neofetch kamoso htop
RUN apt-get install -y wget git
RUN apt-get install -y python3-dev python3-pip virtualenv
RUN apt-get install -y x11-utils
# python3-dev -> Header-Dateien und eine statische Bibliothek für Python ink. Python (Standard)

# # Install of pibooth
# RUN mkdir -p /home/pi/pibooth
# WORKDIR /home/pi/pibooth
# RUN apt-get install -y libsdl2-2.0-0
# RUN wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh && wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/.env && chmod +x gphoto2-updater.sh && sudo ./gphoto2-updater.sh
# RUN apt-get install -y cups
# RUN apt-get install -y libcups2-dev
# RUN apt-get install -y python3-opencv
# RUN pip3 install pibooth[dslr]
# # RUN pip3 install pibooth[dslr,printer]

# Install of photobooth
# RUN apt-get install python3-dev python3-pip virtualenv  
# for PyQt5-GUI
# RUN apt-get update -y
RUN apt-get install -y qt5-default pyqt5-dev pyqt5-dev-tools 
# to use gphoto2
RUN apt-get install -y gphoto2 libgphoto2-dev 
# to use pycups
RUN apt-get install -y libcups2-dev 
# for gphoto2-cffi bindings (libffi6->libffi7)
RUN apt-get install -y libffi7 libffi-dev

WORKDIR /home/ubuntu
# RUN git clone https://github.com/reuterbal/photobooth.git
# WORKDIR /home/pi/photobooth
RUN virtualenv -p python3 --system-site-packages .venv
# RUN source .venv/bin/activate && pip install -e .
# RUN . .venv/bin/activate && pip install -e .
RUN . .venv/bin/activate && pip install -e .
# source -> bash, . -> sh

# PyAutoGUI
RUN apt-get install -y scrot python3-tk
# RUN apt-get install -y scrot python3-tk python3-dev
# RUN source .venv/bin/activate && pip install pyautogui paho-mqtt
RUN . .venv/bin/activate && pip install pyautogui paho-mqtt
# COPY ./PyAutoGUI/ ./

# Bash-Skript für die Ausführung der Photobooth
# RUN echo ".venv/bin/python -m photobooth & .venv/bin/python PyAutoPush.py" > photobooth.sh
# COPY photobooth.cfg /home/pi/photobooth/photobooth.cfg
# COPY background.jpg /home/pi/photobooth/background.jpg

# Install X and xfce
RUN apt-get install -y --no-install-recommends \
  xserver-xorg-input-evdev \
  xinit \
  xfce4 \
  xfce4-terminal \
  x11-xserver-utils \
  dbus-x11 \
  xterm \
  firefox

ENV LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/tegra
ENV XFCE_PANEL_MIGRATE_DEFAULT=1
ENV UDEV=1

# Prevent screen from turning off 1
RUN echo "#!/bin/bash" > /etc/X11/xinit/xserverrc \
  && echo "" >> /etc/X11/xinit/xserverrc \
  && echo 'exec /usr/bin/X -s 0 dpms' >> /etc/X11/xinit/xserverrc

## Prevent screen from turning off 2
RUN echo "xset -dpms & xset s off & xset s noblank &" > /root/.xinitrc

## USB mounten
RUN echo "mkdir /media/usb & mount -t vfat /dev/sda1 /media/usb &" >> /root/.xinitrc 

WORKDIR /home/pi/photobooth
## Start fce4 und photobooth
# RUN echo "startxfce4 & .venv/bin/python -m photobooth" >> /root/.xinitrc

## Start Photobooth und PushButton
RUN echo ".venv/bin/python -m photobooth & .venv/bin/python /home/pi/photobooth/PyAutoPush.py" >> /root/.xinitrc

# RUN echo ".venv/bin/python -m photobooth" >> /root/.xinitrc
# RUN echo "firefox --kiosk -height 1080 -width 1920 --private-window https://tb.iot.ilek.uni-stuttgart.de/" >> /root/.xinitrc



## Start XFCE desktop
# CMD ["startx"]
CMD ["startx", "--", ":1"]