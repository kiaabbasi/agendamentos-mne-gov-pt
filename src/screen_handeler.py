import cv2
import time
import pyautogui
import random
import setings
import tempfile
import os
import logging
from setings import basepath
from typing import Optional,Callable

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

def click_captcha_buttons(break_if_true:Optional[Callable]=None)-> bool:
    """voice capthca
    return False if captcha solved and True if it need to solve
    """
    step=0
    for _ in range (10):
        if break_if_true !=None and break_if_true():
            return False # it mean capthca solved
        elif (pos := find_object_on_screen(f'{basepath}assets/play.png')) != (None, None,0) :
            logging.info("Found play audio button")
            click_on_object(pos[0],pos[1],True)
            step=3
            
            return True
        
        elif (pos := find_object_on_screen(f'{basepath}assets/no_voice_captcha.png',0.7)) != (None, None,0):
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
                time.sleep(0.2)
                top_left, bottom_right = find_chain_objects_on_screen(
                    [f"{basepath}assets/passed.png", f"{basepath}assets/passed_tick.png"]
                )

                if find_object_on_screen(f'{basepath}assets/voice captcha butten.png') != (None, None,0):
                    break
                elif  top_left != (None, None) and bottom_right != (None, None):
                    top_left, bottom_right = find_chain_objects_on_screen(
                        [f"{basepath}assets/passed.png", f"{basepath}assets/passed_tick.png"]
                    )
                    logging.info("Captcha solved already!!")
                    return False
                
            
            step=1
        else:
            logging.info("No target found, retrying...")
            step=0
    
        time.sleep(1)
        
    raise TimeoutError("TimedOut on clicking the capthca's buttons")
        
def which_objects_is_in_page(path_list : list[str]):
    items =[(find_object_on_screen(f,0.2),f)  for f in path_list]
    
    items =sorted(items,key=lambda x: x[0][2],reverse=True)
    
    return items
    
def which_object_is_in_page(path_list : list[str])->tuple[tuple,str]:
    
    sorted_items = which_objects_is_in_page(path_list)
    if sorted_items[0][0][0] is None:
        raise ObjectNotDefindError("No object from the list found on the screen")
    return sorted_items[0]

def find_chain_objects_on_objects(path_list: list[str], threshold=0.8) -> tuple[tuple, tuple]:
    """
    path_list:
        image0 (largest) - تصویر اصلی
        image1 inside image0
        image2 inside image1
        ...
    threshold: similarity threshold for each matching step

    Returns:
        tuple: (top_left, bottom_right) of the last image in the chain within the ORIGINAL image (image0)
        اگر هر مرحله‌ای شکست بخوره: ((None,None), (None,None))
    """

    if len(path_list) < 2:
        raise ValueError("path_list must contain at least two images")

    # تصویر اصلی
    main_image_path = path_list[0]
    main_img = cv2.imread(main_image_path, cv2.IMREAD_GRAYSCALE)
    if main_img is None:
        raise ValueError(f"Could not load main image: {main_image_path}")

    # ROI شروع: کل تصویر
    current_roi = (0, 0, main_img.shape[1], main_img.shape[0])  # x, y, w, h

    for template_path in path_list[1:]:
        template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template_img is None:
            return (None, None), (None, None)

        th, tw = template_img.shape

        x, y, w, h = current_roi
        roi_img = main_img[y:y+h, x:x+w]

        # اگر template از ROI بزرگ‌تر بود → شکست
        if th > roi_img.shape[0] or tw > roi_img.shape[1]:
            return (None, None), (None, None)

        # match فقط داخل ROI
        res = cv2.matchTemplate(roi_img, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # محاسبه قبل از شرط (مشکل اصلی اینجا بود)
        local_top_left = max_loc
        global_top_left = (x + local_top_left[0], y + local_top_left[1])

        # اگر match ضعیف بود → دیباگ + خروج
        if max_val < threshold:
            if DEBUG:
                print("Chain failed on:", template_path, "score:", max_val)
                debug_img = cv2.cvtColor(main_img, cv2.COLOR_GRAY2BGR)
                cv2.rectangle(
                    debug_img,
                    (global_top_left[0], global_top_left[1]),
                    (global_top_left[0] + tw, global_top_left[1] + th),
                    (0, 0, 255), 2
                )
                cv2.imshow("Chain Detection Step (FAILED)", debug_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            return (None, None), (None, None)

        # موفق → ROI بعدی همین ناحیه
        current_roi = (
            global_top_left[0],
            global_top_left[1],
            tw,
            th
        )

        # اگر بخوای هر مرحله رو ببینی (اختیاری)
        if DEBUG:
            debug_img = cv2.cvtColor(main_img, cv2.COLOR_GRAY2BGR)
            cv2.rectangle(
                debug_img,
                (global_top_left[0], global_top_left[1]),
                (global_top_left[0] + tw, global_top_left[1] + th),
                (0, 255, 0), 2
            )
            cv2.imshow("Chain Detection Step", debug_img)
            cv2.waitKey(1)

    # در نهایت مکان آخرین template
    final_x, final_y, final_w, final_h = current_roi
    final_top_left = (final_x, final_y)
    final_bottom_right = (final_x + final_w, final_y + final_h)

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

    