from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as selex
import logging
import screen_handeler
import time
import requests
import voice_to_text , CDP_Contoroler , screen_handeler
import pyautogui
from setings import basepath
class User:
    def __init__(self,username,password,consular_post,category_of_consular_act,consular_act) -> None:
        self.username = username
        self.password = password
        self.consular_post = consular_post
        self.category_of_consular_act=category_of_consular_act
        self.consular_act = consular_act 
        
        
        
class PageHandeler():
    def __init__(self,user:User,wdriver:WebDriver) -> None:
        self.wdriver =wdriver
        self.user = user
                
    def page1(self):
        self.wdriver.get("https://agendamentos.mne.gov.pt/en/login")

        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/main/div/div[2]/div/div[3]/div[2]"))).click() #Go to login with
        try :
            WebDriverWait(self.wdriver,2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/button[2]"))).click() #accept cookies
        except selex.TimeoutException:
            logging.warning("Acsept Coockie field is not defind")

        time.sleep(2)
        self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/div/form/div[1]/div/input').send_keys(self.user.username)#user name fild
        time.sleep(1)
        self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/div/form/div[2]/div/input').send_keys(self.user.password)#password fild
        solve_captcha()
        time.sleep(1)
        self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/div/form/div[5]/button').click() # login button
    def page2(self):
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div[2]/div/a[1]'))).click() #Click on Consular Post

    def page3(self):
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/section/article[1]/div/div/button'))).click() #Click on Consular Post
        elements = self.wdriver.find_elements(
            By.CSS_SELECTOR,
            'div.option.cursor-pointer.pl-4.pr-1\\.5.py-4.border-b.border-zinc-200'
        )
        for e in elements:
            if e.text == self.user.consular_post:
                e.click()
                break
        
        
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/section/article[2]/div/div/button'))).click() #Category of consular act
        
        container = self.wdriver.find_element(
            By.CSS_SELECTOR,
            "div.relative.max-h-\\[10rem\\].overflow-y-auto"
        )
        divs = container.find_elements(By.TAG_NAME, "div")
        
        for j in divs:
            if j.text == self.user.category_of_consular_act:
                j.click()
                break
            
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/section/article[3]/div/div/button'))).click() #Consular act
        container = self.wdriver.find_element(
            By.CSS_SELECTOR,
            "div.relative.max-h-\\[10rem\\].overflow-y-auto"
        )
        divs = container.find_elements(By.TAG_NAME, "div")
        
        for j in divs:
            if j.text == self.user.consular_act:
                j.click()
                break
        
        
        time.sleep(1)
        solve_captcha()
        time.sleep(1)
       
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/div/button[2]'))).click() #Next button

    def page4(self):
        
        e = WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/div/button[2]'))) #Next button
        if self.wdriver.current_url == "https://agendamentos.mne.gov.pt/en/schedule/form/documents":
            e.click()
        else :
            raise ValueError("Wrong elemnt found")

    def page5(self):
        
       
        pass
def solve_captcha():
    
    captcha_is_not_solved= screen_handeler.click_captcha_buttons()
    if captcha_is_not_solved:
        time.sleep(1)
    
        logging.debug(f"url of captcha payload is {CDP_Contoroler.urlfound}")

        response = requests.get(CDP_Contoroler.urlfound, stream=True)
        response.raise_for_status()  # بررسی خطا

        with open("temp.mp3", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        txt = str(voice_to_text.convert("temp.mp3")).lower()
        rs= screen_handeler.find_chain_objects_on_screen([f"{basepath}assets/enter_waht_you_hear.png",f"{basepath}assets/text_box_on_enter_what_you_hear.png"])
        screen_handeler.click_on_object(rs[0],rs[1])
        for k in txt:
            pyautogui.keyDown(k)
            time.sleep(0.05)
            pyautogui.keyUp(k)
            time.sleep(0.05)
        time.sleep(1)
        rs= screen_handeler.find_object_on_screen(f"{basepath}assets/verify.png")
        screen_handeler.click_on_object(rs[0],rs[1])
