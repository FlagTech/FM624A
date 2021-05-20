from machine import freq,SPI,Pin,PWM,ADC,Timer
import time
import LCD
from FlagArcade import *

# 螢幕初始設定
spi = SPI(1, baudrate=40000000, polarity=0, phase=0)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

# 畫頭
screen.drawCircle(65,50,10,LCD.CYAN)
# 畫身體
screen.drawRect(57,60,16,30,LCD.YELLOW)
# 畫眼睛
screen.drawPixel(62,50,LCD.WHITE)
screen.drawPixel(68,50,LCD.WHITE)
# 畫手腳
screen.drawLine(57,60,30,80,LCD.PURPLE)
screen.drawLine(57,90,40,120,LCD.PURPLE)
screen.drawLine(72,60,90,40,LCD.PURPLE)
screen.drawLine(72,90,90,120,LCD.PURPLE)




