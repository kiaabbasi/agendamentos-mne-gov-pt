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
from setings import basepath,PageHandlerSetting
from typing import Dict
import random
import logging

class API():
    base_url = PageHandlerSetting.API_BASE_URL
    sicret_key= PageHandlerSetting.secret_key
    @staticmethod
    def send_reult_to_server(txt:str):
        url = API.base_url +"send"
        logging.debug(f"requesting {url}/{txt}")
        params = {
            "message": f"{txt}"
        }

        headers = {
            "x-api-key": f"{API.sicret_key}"
        }

        response = requests.get(url, params=params, headers=headers)

        rs=response.json()
        
        return rs["status"]==200
        

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

        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/main/div/div[2]/div/div[3]/div[2]"))).click() #Go to login with
        try :
            WebDriverWait(self.wdriver,2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/button[2]"))).click() #accept cookies
        except selex.TimeoutException:
            logging.warning("Acsept Coockie field is not defind")

        time.sleep(2)
        logging.debug("typing username...")
        self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/div/form/div[1]/div/input').send_keys(self.user.username)#user name fild
        time.sleep(1)
        logging.debug("typing passwrod...")
        self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/div/form/div[2]/div/input').send_keys(self.user.password)#password fild
        logging.debug("handleing captcha...")
        solve_captcha()
        time.sleep(1)
        logging.debug("Clicking on Next button...")
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="main"]/div/div[2]/div/form/div[5]/button'))).click()# login button
       
    def page2(self):#https://agendamentos.mne.gov.pt/en/schedule
        WebDriverWait(self.wdriver,15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div[2]/div/a[1]'))).click() #Click on Consular Post

    def page3(self):
        def captcha_solved_check()->bool:
            try:
                if self.wdriver.current_url == "https://agendamentos.mne.gov.pt/en/schedule/form/consular":
                    e =self.wdriver.find_element(By.XPATH,"/html/body/div[1]/div/div/main/div/section[3]/div/form/section/article[4]")
                    
                return False
            except selex.NoSuchElementException :
                return True
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
        
        
        time.sleep(1.5)
        solve_captcha(break_if_true=captcha_solved_check)
        time.sleep(1)
       
        WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/div/button[2]'))).click() #Next button

    def page4(self):
        
        e = WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/section[3]/div/form/div/button[2]'))) #Next button
        if self.wdriver.current_url == "https://agendamentos.mne.gov.pt/en/schedule/form/documents":
            e.click()
        else :
            raise ValueError("Wrong elemnt found")

    def page5(self,deley_start,deley_end,register =False):
        #TODO complet this
        rtn=[]
        if deley_start > deley_end or deley_start<0:
            raise ValueError("deley_start must be smaler than deley_end")
        
        previous_month = WebDriverWait(self.wdriver,10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="main"]/div/section[3]/section/form/section[1]/article/div/div/div[1]/div/div/div/div[2]/button[1]')))[0] #previous-month
        next_month = WebDriverWait(self.wdriver,10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="main"]/div/section[3]/section/form/section[1]/article/div/div/div[1]/div/div/div/div[2]/button[2]')))[0] #next-month
        going_forward = True
        while True :
            dict_result:Dict={"user_registered":False}
            
            month_and_year=self.wdriver.find_element(By.XPATH,'/html/body/div[1]/div/div/main/div/section[3]/section/form/section[1]/article/div/div/div[1]/div/div/div/div[1]').text
            dict_result["month_and_year"] =month_and_year
            
            all_dates= self.wdriver.find_elements(By.CSS_SELECTOR,'button[name="day"]:not([disabled])')
            days=[h.text for h in all_dates]
            dict_result["days"] = days
            if len(days) > 0:
                API.send_reult_to_server(f"🟢{month_and_year}\n{days}")
            else :
                API.send_reult_to_server(f"🔴{month_and_year} No Day availble")
            if register:
                # Click first date avalble
                all_dates[0].click()    
                WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.NAME, 'hour-slot'))).click() # Hour
                
                self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/section[3]/section/form/div[2]/button[2]').click()
                dict_result["user_registered"] = True
                API.send_reult_to_server(f"{self.user.username} has ben registerd on {month_and_year}-{all_dates[0]}")
                break
            
            if going_forward and  next_month.get_attribute("disabled") !="true":
                next_month.click()
            elif not going_forward and previous_month.get_attribute("disabled") !="true":
                previous_month.click()
                
            else :
                going_forward = not going_forward            
            
            time.sleep(random.randint(deley_start,deley_end))
            
            rtn.append(dict_result)
        return rtn
            


def solve_captcha(*args, **kwargs):
    
    captcha_is_not_solved= screen_handeler.click_captcha_buttons(*args, **kwargs)
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
        
logging.getLogger().setLevel(logging.DEBUG)