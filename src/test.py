import pyautogui
import time
for i in range (100) :
    a =pyautogui.screenshot()
    a.save(f"test{i}.png")
    time.sleep(1)
    print(i)