from machine import SPI
import LCD
# from FlagArcade import *

# 螢幕初始設定
spi = SPI(1, baudrate=40000000)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

# 文字顏色調整
screen.text(10, 10, "Hello World")
screen.text(10, 30, "Hello World", LCD.YELLOW)
screen.text(10, 50, "Hello World", LCD.RED, screen.rgbcolor(100,100,100))
screen.text(10, 70, "Hello World", screen.rgbcolor(0,200,0), screen.rgbcolor(150,0,150))

