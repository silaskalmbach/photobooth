# Aktuell nur unter X11
# cd /home/silas/PhotoFrame/photobooth/RaspiButtons
#. /home/silas/PhotoFrame/photobooth/.venv/bin/activate
# python3 PyRaspiAutoPush.py 
# cd /home/silas/PhotoFrame/photobooth/RaspiButtons && . /home/silas/PhotoFrame/photobooth/.venv/bin/activate && python3 PyRaspiAutoPush.py 
# /home/silas/PhotoFrame/photobooth/.venv/bin/python3 /home/silas/PhotoFrame/photobooth/RaspiButtons/PyRaspiAutoPush.py 
# pip install PyAutoGUI
# pip install gpiozero

import pyautogui
from gpiozero import Button
import time

def press_button1():
    # Press Escape
    # pyautogui.press('E')
    pyautogui.press('esc')

def press_button2():
    # pyautogui.press('enter') 
    # Press tab
    # pyautogui.press('S')
    pyautogui.press('tab')
    # Press space
    pyautogui.press('space')



def main():
    button1 = Button(14)
    button2 = Button(23)

    while True:
        if button1.is_pressed:
            press_button1()
            # print("Taster1 ist gedrückt!")
            time.sleep(0.5) 
        elif button2.is_pressed:
            # print("Taster2 ist gedrückt!")  
            press_button2()
            time.sleep(0.5)
        # else:
        #     print("Taster sind nicht gedrückt!")

if __name__ == '__main__':
    main()
