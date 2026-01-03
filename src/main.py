from selenium  import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import logging 

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import CDP_Contoroler
import PageHandler
import UserManager
import os

from screen_handeler import ObjectNotDefindError

from selenium.common import exceptions as slex

logging.getLogger().setLevel(logging.WARNING)
logger = logging.getLogger("__main__")
logger.setLevel(logging.DEBUG)

# هندلر مستقل برای __main__
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False
logger.info("App Started")


        
        
def initialize_browser(proxy)->WebDriver:
    
    
    options = Options()

    options.add_argument(rf"--user-data-dir=C:\Users\{os.getlogin()}\AppData\Local\Google\Chrome\User Data\Default")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-infobars")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--remote-allow-origins=*")

    if proxy !="":
        options.add_argument(f"--proxy-server={proxy}")
    return  webdriver.Chrome(
        service=Service(),
        options=options,

    )


proxies=[
    "",
    "127.0.0.1:10001",
    "127.0.0.1:10002",
    "127.0.0.1:10003",
    "127.0.0.1:10004",
    "127.0.0.1:10005",
    "127.0.0.1:10006",
    "127.0.0.1:10007",
    "127.0.0.1:10008",
    "127.0.0.1:10009",
    "127.0.0.1:10010",
    ]     
if __name__ == "__main__":
    driver:WebDriver|None=None
    prx_indx=0
    while True:
        try:
            
            # Load Browser
            for i in range(3):
                try :
                    logger.info("Initializing Chrome WebDriver···")
                    driver = initialize_browser(proxies[prx_indx])
                    logger.info("Chrome WebDriver initialized successfully ")
                    break
                
                except Exception as e:
                    logger.error(f"Failed to initialize browser: {e}", exc_info=True)
            
                time.sleep(2)
                logger.info(f"Retrying {i+1}...")
                
            else:
                logger.critical("faild to load browser we cant continue")
                exit(1)
                
            # Connect To CDP
            for i in range(3):
                try :
                    logger.info("Locking for Chrome with Open CDP···")
                    main_browser = CDP_Contoroler.ChromeBrowserCDP.find_browser_and_create_CDP_object()
                    logger.info("Connecting to CDP···")
                    main_browser.connect()
                    logger.info("Connected to CDP ✔ ")
                    time.sleep(1)
                    logger.debug("set_discover_targets on")
                    main_browser.run_on_discovered_target.append({"method": "Network.enable", "params": {"maxPostDataSize": 10485760}})
                    main_browser.set_discover_targets()
                    break
                except Exception as e:
                    logger.error(f"Failed to connect to CDP: {e}", exc_info=True)
                
                logger.info(f"Retrying to Connect CDP{i+1}...")
            else :
                logger.critical("Faild to connect to CDP can not continue")
                exit(1)
                
                
            """u = UserManager.User(
                "khodamorad.mandegarihassanabad@gmail.com",
                "@912119427Aa",
                "Secção Consular da Embaixada de Portugal em Teerão",
                "Notary",
                "Certification of a signature"
                )"""
            for u in UserManager.get_all_users():
                try:
                    driver.get("https://agendamentos.mne.gov.pt/en/login")
                    page_handeler = PageHandler.PageHandeler(u,driver)     
                    #https://agendamentos.mne.gov.pt/en/login?type=session_expired
                    if driver.current_url == "https://agendamentos.mne.gov.pt/en/login":
                        page_handeler.page1()
                        time.sleep(1)
                        
                
                    page_handeler.page2()
                    time.sleep(1)
                    page_handeler.page3()
                    time.sleep(1)
                    page_handeler.page4()
                    time.sleep(1)
                    r= page_handeler.page5(5,10,False)
                    PageHandler.API.send_reult_to_server(str(r))
                    
               
                   
                
                except slex.TimeoutException as e :
                    print("elemnt_not_defind")
                except Exception as e:
                    logger.error(e,exc_info=True)
                finally :
                    driver.delete_cookie("user_consent")
                    driver.delete_cookie("cookiesession1")
                    driver.execute_script("window.localStorage.clear();")
                        
        finally : 
            if driver != None:
                driver.quit()
                
        prx_indx+=1 
        if prx_indx < len(proxies):
            pass
        else :
            prx_indx = 0   
        time.sleep(3)