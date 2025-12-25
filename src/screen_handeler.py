import cv2
import time
import numpy as np
import pyautogui
import random
import setings
import tempfile
import os
import logging
from setings import basepath


DEBUG =setings.DEBUG

class ObjectNotDefindError(Exception):
    pass

def find_object_on_object(path_to_template_image: str, path_to_main_image:str, threshold=0.8):
    main_img = cv2.imread(path_to_main_image, cv2.IMREAD_GRAYSCALE)
    template_img = cv2.imread(path_to_template_image, cv2.IMREAD_GRAYSCALE)
    
    
    th, tw = template_img.shape
    ih, iw = main_img.shape

    # اگر template بزرگ‌تر از تصویر باشد
    if th > ih or tw > iw:
        print("Template is larger than screenshot")
        return None, None,0
    
    
    res = cv2.matchTemplate(main_img, template_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
    
    if max_val < threshold:
        return None, None,0


    top_left = max_loc
    bottom_right = (top_left[0] + tw, top_left[1] + th)

    if DEBUG:
        debug_img = main_img.copy()
        cv2.rectangle(debug_img, top_left, bottom_right, (0, 0, 255), 2)
        cv2.imshow("Detected", debug_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return top_left, bottom_right,max_val # max_val is the similarity score

    
    
def find_object_on_screen(path_to_template_image: str, threshold=0.8):
    
    screenshot = pyautogui.screenshot()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        screenshot.save(tmp_path)

    try:
        result = find_object_on_object(path_to_template_image, tmp_path, threshold)
    finally:
        os.remove(tmp_path)

    return result

    
    

def click_on_object(top_left , bottom_right,center=False):
    x,y=0,0
    if center:
        x = (top_left[0] + bottom_right[0]) // 2
        y = (top_left[1] + bottom_right[1]) // 2
    else:
        x,y = random.randint(top_left[0]+2,bottom_right[0]-2), random.randint(top_left[1]+2,bottom_right[1]-2)
    pyautogui.click(x,y)

def click_captcha_buttons()-> bool:
    """voice capthca
    return False if captcha solved and True if it need to solve
    """
    step=0
    for _ in range (10):
        if (pos := find_object_on_screen(f'{basepath}assets/play.png')) != (None, None,0) :
            logging.info("Found play audio button")
            click_on_object(pos[0],pos[1],True)
            step=3
            
            return True
        
        elif (pos := find_object_on_screen(f'{basepath}assets/no_voice_captcha.png')) != (None, None,0):
            raise ObjectNotDefindError("voice Capthca is not availble")
        
        elif (pos := find_object_on_screen(f'{basepath}assets/voice captcha butten.png')) != (None, None,0):
            logging.info("Found voice captcha button")
            click_on_object(pos[0],pos[1])
            step=2
        
        elif (pos := find_object_on_screen(f'{basepath}assets/passed.png')) != (None, None,0)  :
            logging.info("Captcha solved already!")
            return False
        elif step==0 and (pos := find_object_on_screen(f'{basepath}assets/im not robot defult.png')) != (None, None,0):
            logging.info("Found im not robot button")
            click_on_object(pos[0],pos[1])
            for i in range(10):
                top_left, bottom_right = find_chain_objects_on_screen(
                    [f"{basepath}assets/passed.png", f"{basepath}assets/passed_tick.png"]
                )

                if find_object_on_screen(f'{basepath}assets/voice captcha butten.png') != (None, None,0):
                    break
                elif  top_left != (None, None) and bottom_right != (None, None):
                    logging.info("Captcha solved already!!")
                    return False
                
            
            step=1
        else:
            logging.info("No target found, retrying...")
            step=0
    
        time.sleep(1)
        
    raise TimeoutError("TimedOut")
        
def which_objects_is_in_page(path_list : list[str]):
    items =[(find_object_on_screen(f,0.2),f)  for f in path_list]
    
    items =sorted(items,key=lambda x: x[0][2],reverse=True)
    
    return items
    
def which_object_is_in_page(path_list : list[str])->tuple[tuple,str]:
    
    sorted_items = which_objects_is_in_page(path_list)
    if sorted_items[0][0][0] is None:
        raise ObjectNotDefindError("No object from the list found on the screen")
    return sorted_items[0]

def find_chain_objects_on_objects(path_list : list[str], threshold=0.8)-> tuple[tuple,tuple]:
    """
    path_list:
        image0 (largest)
        image1 inside image0
        image2 inside image1
    threshold: similarity threshold for each matching step
    Returns:
        tuple: (top_left, bottom_right) of the last image in the chain within the first image
    """ 

    if len(path_list)<2:
        raise ValueError("path_list must contain at least two images")
    
    last_image_path = path_list[0]
    
    top_left_offset_x=0
    top_left_offset_y=0
    
   
    for path in path_list[1:]:
        top_left,bot_right,score= find_object_on_object(
            path_to_main_image=last_image_path,
            path_to_template_image=path,
            threshold= threshold
        )
        if top_left is None or bot_right is None:
            return (None,None),(None,None)
        last_image_path = path

        top_left_offset_x += top_left[0]
        top_left_offset_y += top_left[1]
        
    last_template = cv2.imread(path_list[-1], cv2.IMREAD_GRAYSCALE)
    h, w = last_template.shape

    final_top_left = (top_left_offset_x, top_left_offset_y)
    final_bottom_right = (top_left_offset_x + w, top_left_offset_y + h)

    return final_top_left, final_bottom_right

    
    
def find_chain_objects_on_screen(path_list : list[str], threshold=0.8)-> tuple[tuple,tuple]:
    
    screenshot = pyautogui.screenshot()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        screenshot.save(tmp_path)

    try:
        path_list.insert(0, tmp_path)
        result = find_chain_objects_on_objects(path_list, threshold)
    finally:
        os.remove(tmp_path)

    return result

    