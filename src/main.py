from selenium  import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import logging 

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import CDP_Contoroler
import PageHandler


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


        
        
def initialize_browser()->WebDriver:
    
    
    options = Options()

    options.add_argument("--user-data-dir=C:\\Users\\HRT\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-infobars")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--remote-allow-origins=*")

    
    return  webdriver.Chrome(
        service=Service(),
        options=options,

    )



if __name__ == "__main__":
    driver:WebDriver|None=None

    try:
        
        # Load Browser
        for i in range(3):
            try :
                logger.info("Initializing Chrome WebDriver···")
                driver = initialize_browser()
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
            
       
        u = PageHandler.User(
            "khodamorad.mandegarihassanabad@gmail.com",
            "@912119427Aa",
            "Secção Consular da Embaixada de Portugal em Teerão",
            "Notary",
            "Certification of a signature"
            )
        
     
        page_handeler = PageHandler.PageHandeler(u,driver)     
        #https://agendamentos.mne.gov.pt/en/login?type=session_expired
        if  driver.current_url =="https://agendamentos.mne.gov.pt/en/login":
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
        
        input("the end")
    finally : 
        if driver != None:
            #driver.quit()
            pass
            