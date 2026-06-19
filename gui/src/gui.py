from tkinter import Tk
import tkinter as tk
from gui.src import custom_widgets as cw


root: Tk = tk.Tk()
root.title('Substrate Stepper Rotation')

# Marked by comment characters,the following block was taken from https://www.pythontutorial.net/tkinter/tkinter-window/
window_width = 720
window_height = 540

screen_width: int = root.winfo_screenwidth()
screen_height: int = root.winfo_screenheight()

center_x: int = int(screen_width/2 - window_width / 2)
center_y: int = int(screen_height/2 - window_height / 2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

######## Now the GUI is centered in the window upon open FIX THIS, THIS IS NO LONGER REQUIRED. WE WANT THREE SEPERATE WINDOWS NOW

ConstantSpeed: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=root,
    label_text="Angular Speed (RPM)",
    button_text="Send"
    )
ConstantSpeed.pack(pady=20)

ConstantSpeedToggle: cw.OnOffToggleNum = cw.OnOffToggleNum(master=root)
ConstantSpeedToggle.pack(pady=20)

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()