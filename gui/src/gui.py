import tkinter as tk
from tkinter import Tk, ttk

from gui.src import custom_widgets as cw

root: Tk = tk.Tk()
root.title("Electrode Chamber Control Interface")

# Marked by comment characters, the following block was taken from https://www.pythontutorial.net/tkinter/tkinter-window/
# It centers the GUI in the middle of the screen upon opening.
#
window_width = 720
window_height = 540

screen_width: int = root.winfo_screenwidth()
screen_height: int = root.winfo_screenheight()

center_x: int = int(screen_width / 2 - window_width / 2)
center_y: int = int(screen_height / 2 - window_height / 2)

root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

notebook: ttk.Notebook = ttk.Notebook(master=root)
notebook.pack(pady=10, expand=True, fill="both")

linear_tab: ttk.Frame = ttk.Frame(master=notebook)

constant_speed: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=linear_tab, label_text="Angular Speed (RPM)", button_text="Send"
)
constant_speed.pack(pady=20)

constant_speed_toggle: cw.OnOffToggleNum = cw.OnOffToggleNum(master=linear_tab)
constant_speed_toggle.pack(pady=20)

rotation_tab: ttk.Frame = ttk.Frame(master=notebook)
mirror_tab: ttk.Frame = ttk.Frame(master=notebook)
serial_tab: ttk.Frame = ttk.Frame(master=notebook)

notebook.add(child=linear_tab, text="Target Linear Motion")
notebook.add(child=rotation_tab, text="Substrate Rotation")
notebook.add(child=mirror_tab, text="Laser Mirror Planar Motion")
notebook.add(child=serial_tab, text="Serial Connection")

try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
