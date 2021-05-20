from machine import freq,SPI,Pin,PWM,ADC,Timer
import time
import LCD
from FlagArcade import *

# 螢幕初始設定
spi = SPI(1, baudrate=40000000, polarity=0, phase=0)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

h1=(
b"  111   111  "
b" 1   1 1   1 "
b"1     1     1"
b"1           1"
b"1           1"
b" 1         1 "
b"  1       1  "
b"   1     1   "
b"    1   1    "
b"     1 1     "
b"      1      "
)

heart= Character(h1, 13, 11, screen, LCD.RED)
heart.show(20,20)
heart.plot()
