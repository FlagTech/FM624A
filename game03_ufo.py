from machine import ADC,SPI,PWM,Pin,freq
from FlagArcade import *
import LCD

# 螢幕初始設定
spi = SPI(1, baudrate=40000000)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

# 按鈕腳位設定
adc = ADC(0)

# 蜂鳴器腳位與強度設定
buzzer = PWM(Pin(4))
amp = 512

# 設計遊戲音效
def ding():
    buzzer.freq(988)
    buzzer.duty(amp)
    time.sleep(.05)
    buzzer.duty(0)

def toot():
    buzzer.freq(494)
    buzzer.duty(amp)
    time.sleep(.01)
    buzzer.duty(0)
    
def buzz():
    buzzer.freq(247)
    buzzer.duty(amp)
    time.sleep(.5)
    buzzer.duty(0)

# 建立遊戲角色
h1=(
b"        1   1111    "    
b"       1    1       "    
b"      1111111111111 "    
b"            1    1  "
b"         1111   1   "
b"1           1       "
b"  1     1111111111  "
b" 1 11111111     1 1 "
b" 1   1111 1     1  1"
b"       1111     1  1"
b"       1111     1  1"
b"        111111111111"
b"          1    1    "
b"          1    1  1 "
b"        1111111111  "
)

h2=(
b"        1111   11   "    
b"         11   11 1  "    
b"      1    111    1 "    
b"       1 11   11    "
b"        11   1111   "
b"1           1       "
b" 1      1111111111  "
b"  111111111     1 1 "
b" 1   1111 1     1  1"
b"       1111     1  1"
b"       1111     1  1"
b"        111111111111"
b"          1    1    "
b"          1    1  1 "
b"        1111111111  "
)

u1=(
b"                 "
b"         1       "
b"         1       "
b"       11111     "
b"     11     11   "
b"    11       11  "
b"    11       11  "
b"   1111111111111 "
b"  111 11 11 11 11"
b"   1111111111111 "
b"    111 1 1 111  "
b"     1   1   1   "
)

u2=(
b"         1       "
b"        1 1      "
b"         1       "
b"       11111     "
b"     11     11   "
b"    11       11  "
b"    11       11  "
b"   1111111111111 "
b"  11 11 11 11 111"
b"   1111111111111 "
b"    1 1 111 1 1  "
b"     1   1   1   "
)

bbb=(
b"11   11   11 "
b" 11   11   11"
b"11   11   11 "
)

helicopter = Character([h1,h2], 20, 15, screen, LCD.BLUE)
ufo = Character([u1,u2], 17, 11, screen, LCD.YELLOW)
bullet = Character(bbb,13,3, screen, LCD.RED)
bullet.x=150

# 宣告全域變數
end = False
score=0

# 建立常用函式
def resetGame():
    global end,score
    helicopter.show(0,100)
    ufo.show(140,randint(30,150))
    bullet.show(140,0)
    screen.text(30,70, "Game Over",LCD.BLACK)
    end=False
    score=0

def printScore():
    global score 
    screen.text(10, 5,"score:"+str(score)+'   ')
    
resetGame()
printScore()
    
while True:
    key=getKey(adc.read())
    if not end:
        # 控制直升機
        if key=='u' and helicopter.y>20:
            helicopter.move(0,-3)
            toot()
        elif key=='d' and helicopter.y<150:
            helicopter.move(0,5)
            toot()
        else:
            helicopter.plot()
            
        # 發射子彈
        if key=='m' and bullet.x>=130:
            ding()
            bullet.show(helicopter.x+10,helicopter.y+10)
        if bullet.x<130 :
            bullet.move(10,0)

        # 幽浮逼近
        ufo.move(-2,randint(-1-score,1+score))
        if ufo.y>140 : ufo.y=140
        if ufo.y< 30 : ufo.y=30
        
        # 漏打幽浮扣分
        if ufo.x<-20:
            buzz()
            score-=1
            printScore()
#             ufo.hide()
            ufo.show(130,randint(30,150))
            
        # 擊中幽浮得分
        if ufo.touch(bullet) :
            ding()
            score+=1
            printScore()
#             ufo.hide()
            ufo.show(130,randint(30,150))
            bullet.show(140,100)
            
        # 碰撞墜毀，遊戲結束
        if helicopter.touch(ufo) :
            buzz()
            screen.text(30,70, "Game Over",LCD.YELLOW)
            end=True
        if score<0:
            screen.text(30,70, "Game Over",LCD.YELLOW)
            end=True
            
    # 遊戲重啟
    if end :
        if key=="rst":
            resetGame()
            printScore()
    # 切換靜音
    if key=="set" :
        if amp == 512 :
            amp = 0
        else :
            amp = 512           
        


