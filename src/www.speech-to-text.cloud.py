from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time


options = Options()
options.binary_location="D:\\apps\\fire fix\\firefox.exe"


driver = webdriver.Firefox(options=options,service=Service("D:\\python codes\\geckodriver.exe"))
driver.execute_script("Object.defineProperty(navigator,'webdriver',{get : ()=> undefined})")
driver.get("https://www.speech-to-text.cloud/")
driver.execute_script("Object.defineProperty(navigator,'webdriver',{get : ()=> undefined})")



file_input =WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID, "upload")))


file_path = "C:\\Users\\HRT\\Documents\\payload3.mp3"
file_input.send_keys(file_path) 


status_lable = driver.find_element(By.ID,"status")

time_out = 10
for i in range(time_out) :
    print(status :=status_lable.text)
    if status == "Release the transcript or Transcribe More & Save" or status == "Transcription finished.":
        break
        
    time.sleep(1)
else :
    if status_lable.text == "Transcription finished.":
        result= driver.find_element(By.XPATH,"//*[@id='transcript']/div/div[2]").text
        print(result)
