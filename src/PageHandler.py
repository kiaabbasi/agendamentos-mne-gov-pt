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
from UserManager import User



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
        #if self.wdriver.current_url == "https://agendamentos.mne.gov.pt/en/schedule/form/documents":
        e.click()
        #else :
            #raise ValueError("Wrong elemnt found")

    def page5(self,deley_start,deley_end,register =False):        
        rtn=[]
        if deley_start > deley_end or deley_start<0:
            raise ValueError("deley_start must be smaler than deley_end")
        
        going_forward = True
        month_forward_clicked=0
        while True :
            dict_result:Dict={"user_registered":False}
            
                
            month_and_year=WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/main/div/section[3]/section/form/section[1]/article/div/div/div[1]/div/div/div/div[1]'))).text 
            
            dict_result["month_and_year"] =month_and_year
            
            all_dates= self.wdriver.find_elements(By.CSS_SELECTOR,'button[name="day"]:not([disabled])')
            days=[h.text for h in all_dates]
            dict_result["days"] = days
            try :
                if len(days) > 0:
                    API.send_reult_to_server(
                        f"🟢 {month_and_year}\n"
                        f"consular_post : {self.user.consular_post}\n"
                        f"category_of_consular_act : {self.user.category_of_consular_act}\n"
                        f"consular_act : {self.user.consular_act}\n"
                        f"available days : {', '.join(map(str, days))}"
                    )
                else:
                    API.send_reult_to_server(
                        f"🔴 {month_and_year} No day available\n"
                        f"consular_post : {self.user.consular_post}\n"
                        f"category_of_consular_act : {self.user.category_of_consular_act}\n"
                        f"consular_act : {self.user.consular_act}"
                    )
                    
            except requests.ConnectionError :
                logging.error("Faild to send result to api")
            if len(all_dates)>0 and  register:
                # Click first date avalble
                all_dates[0].click()    
                WebDriverWait(self.wdriver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="hour-slot"]:not([disabled])'))).click() # Hour
                
                self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/section[3]/section/form/div[2]/button[2]').click()#register button
                dict_result["user_registered"] = True
                API.send_reult_to_server(f"{self.user.username} has ben registerd on {month_and_year}-{all_dates[0]}")
                break
            time.sleep(random.randint(deley_start,deley_end))
            try :
                previous_month = WebDriverWait(self.wdriver,4).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="main"]/div/section[3]/section/form/section[1]/article/div/div/div[1]/div/div/div/div[2]/button[1]')))[0] #previous-month
                next_month = WebDriverWait(self.wdriver,4).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="main"]/div/section[3]/section/form/section[1]/article/div/div/div[1]/div/div/div/div[2]/button[2]')))[0] #next-month
                for _ in range(3):
                    if going_forward and  next_month.get_attribute("disabled") !="true":
                        next_month.click()
                        month_forward_clicked+=1
                        if month_forward_clicked > PageHandlerSetting.max_month_check:
                            going_forward = not going_forward
                        break
                    elif not going_forward and previous_month.get_attribute("disabled") !="true":
                        previous_month.click()
                        month_forward_clicked-=1
                        if month_forward_clicked <= 0:
                            going_forward = not going_forward
                        break
                        
                    else :
                        going_forward = not going_forward   
            except selex.TimeoutException:
                if self.wdriver.current_url == "https://agendamentos.mne.gov.pt/en/schedule/form/calendar":
                    
                    self.wdriver.find_element(By.XPATH,'//*[@id="main"]/div/section[3]/section/form/div[2]/button[1]').click() #Back button
                    self.page4()
                else :
                    break
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
        for i in range(4):
            rs= screen_handeler.find_chain_objects_on_screen([f"{basepath}assets/enter_waht_you_hear.png",f"{basepath}assets/text_box_on_enter_what_you_hear.png"])
            if rs != ((None,None),(None,None)):
                screen_handeler.click_on_object(rs[0],rs[1],center=True)
                break
            time.sleep(1)
        else:
            raise Exception("Faild to click elemnt")
        for k in txt:
            pyautogui.keyDown(k)
            time.sleep(0.05)
            pyautogui.keyUp(k)
            time.sleep(0.05)
        time.sleep(1)
        
        for i in range(4):
            rs= screen_handeler.find_object_on_screen(f"{basepath}assets/verify.png")
            if rs != (None,None):
                screen_handeler.click_on_object(rs[0],rs[1],center=True)
                break
            time.sleep(1)
        else:
            raise Exception("Faild to click elemnt")
        
logging.getLogger().setLevel(logging.DEBUG)