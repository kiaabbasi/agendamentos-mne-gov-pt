import pyautogui
import time
import random

time.sleep(3)

screen_width, screen_height = pyautogui.size()
screen_width-=30
screen_height -= 20
# 3. تعداد خطوطی که میخوای بکشه
num_lines = 10

y=200
x=10
pyautogui.moveTo(x,y)
for i in range(0,num_lines,2):
    pyautogui.mouseDown()
    pyautogui.moveTo(screen_width,y,1)#->
    y+=50
    pyautogui.moveTo(screen_width,y,1)#|
    pyautogui.moveTo(x,y,1)#<-
    y+=50
    pyautogui.moveTo(x,y,1)#|
    
    pyautogui.mouseUp()