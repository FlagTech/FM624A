from machine import ADC, SPI, PWM, Pin, freq, reset
from FlagArcade import *
import LCD
import time

# 設定 CPU 頻率
freq(160000000)

# 螢幕初始設定
spi = SPI(1, baudrate=40000000)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

# 按鈕腳位設定
adc = ADC(0)

# 蜂鳴器腳位與強度設定
buzzer = PWM(Pin(4))
buzzer.freq(1000)

def ding():
    buzzer.duty(100)
    time.sleep(.05)
    buzzer.duty(0)

# 顯示標題與按鍵說明
screen.text(20, 15, "Python Game")
screen.drawFastHLine(0, 32, 128, LCD.GREEN)
screen.text(10, 35, "Up Dn: select")
screen.text(10, 45, "Right: enter")
screen.drawFastHLine(0, 55, 128, LCD.GREEN)

# 顯示選單項目
# 請注意! filename 不要放 .py
items =(
    {"title": "Car", "filename": "game01_car"} ,
    {"title": "Cat", "filename": "game02_cat"} ,
    {"title": "UFO", "filename": "game03_ufo"} ,
    {"title": "Tank", "filename": "game04_tank"} ,
    {"title": "Bicycle", "filename": "game05_bicycle"} ,
    #{"title": "Down Floor", "filename": "game06_downfloor"} ,
    )
item_x = 20
item_y = 70
item_spaces = 17  # 每個項目的間隔 (以左上角為準)
for n, item in enumerate(items):
    screen.text(item_x, item_y+item_spaces*n,
            "{}.{}".format(n+1, item["title"]))

# 使用者操作箭頭
arrow_x = 10
selected = 1
selected_last = 6  # 與 selected 不同, 開機後迴圈第一輪才會畫箭頭
selected_max = len(items)
while True:

    if not selected == selected_last:
        screen.text(arrow_x,
            item_y+(selected_last-1)*item_spaces, " ")
        screen.text(arrow_x,
            item_y+(selected-1)*item_spaces, ">", LCD.YELLOW)
        selected_last = selected

    key=getKey(adc.read())
    
    if key == 'd' or key == 'u':
        time.sleep(0.2)
        ding()

        selected_last = selected
        if key == 'd':
            selected += 1
        elif key == 'u':
            selected -= 1

        if selected < 1:
            selected = selected_max
        if selected > selected_max:
            selected = 1

    elif key == 'r':
        ding()
        n = selected - 1
        game_filename = items[n]["filename"]
        print("準備進入遊戲: " + game_filename)
        #__import__(game_filename)
        
        with open("autorun", 'w') as f:
            f.write(game_filename)

        screen.clearLCD()
        screen.text(20, 70, items[n]["title"])
        screen.text(20, 80, "Loading...")
        time.sleep(1)
        reset()
        while True:
            pass