cd ~
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
chmod +x LCD35-show
sudo ./LCD35-show

# Corrigir overlay no config.txt
sudo nano /boot/config.txt
# comente a linha antiga:
#dtoverlay=tft35a:rotate=90
# adicione:
dtoverlay=piscreen,drm

# Fixar boot gráfico
sudo systemctl set-default graphical.target

# Reiniciar
sudo reboot
 

sudo nano /boot/config.txt
#dtoverlay=tft35a:rotate=90
dtoverlay=piscreen,drm


sudo apt install raspi-config raspi-utils rpi-eeprom raspinfo

sudo apt install --no-install-recommends raspberrypi-ui-mods lxsession lightdm pi-greeter

sudo systemctl set-default graphical.target
sudo reboot

sudo systemctl set-default graphical.target
systemctl status lightdm


sudo raspi-config
System Options → Boot / Auto Login → Desktop Autologin.

Pino físico Pi
2	5V	—	2 (5V Power)
6	GND	—	6 (Ground)
18	RS/DC	GPIO 24	18
22	RST	GPIO 25	22
19	SPI MOSI	GPIO 10	19
23	SPI SCLK	GPIO 11	23
24	SPI CSCE0	GPIO 8	24
