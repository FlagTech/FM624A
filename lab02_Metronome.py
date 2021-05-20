from machine import Pin,PWM 
import time
from FlagArcade import *

buzzer = PWM(Pin(12))
buzzer.freq(988)

while True:
    buzzer.duty(512)
    time.sleep(.05)
    buzzer.duty(0)
    time.sleep(.95)
