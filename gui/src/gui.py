import tkinter as tk
from tkinter import Tk, ttk

from gui.src import custom_widgets as cw
from gui.src.serial_monitor import serial_worker

ser: serial_worker = serial_worker(baudrate=115200, timeout=1)
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

linear_max_speed: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=linear_tab, label_text="Max Speed (step/s)", button_text="Send"
)
linear_max_speed.pack(pady=5)

acceleration: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=linear_tab, label_text="Acceleration (step/s^2)", button_text="Send"
)
acceleration.pack(pady=5)

final_position: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=linear_tab, label_text="Final Postion (step)", button_text="Send"
)
final_position.pack(pady=10)

move_to: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=linear_tab, label_text="Move to (steps)", button_text="Send"
)
move_to.pack(pady=10)

move: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=linear_tab, label_text="Move (steps)", button_text="Send"
)
move.pack(pady=5)

lin_direction: cw.BooleanRadios = cw.BooleanRadios(
    parent=linear_tab, left_text="In", right_text="Out"
)
lin_direction.pack(pady=5)

home_toggle_buttons: cw.HomeAndToggle = cw.HomeAndToggle(parent=linear_tab)
home_toggle_buttons.pack(pady=5)


rotation_tab: ttk.Frame = ttk.Frame(master=notebook)

constant_speed: cw.LabelEntryButton = cw.LabelEntryButton(
    parent=rotation_tab, label_text="Angular Speed (RPM)", button_text="Send"
)
constant_speed.pack(pady=5)

constant_speed_toggle: cw.OnOffToggle = cw.OnOffToggle(master=rotation_tab)
constant_speed_toggle.pack(pady=5)

rot_direction: cw.BooleanRadios = cw.BooleanRadios(
    parent=rotation_tab, left_text="In", right_text="Out"
)
rot_direction.pack(pady=5)


mirror_tab: ttk.Frame = ttk.Frame(master=notebook)


serial_tab: ttk.Frame = ttk.Frame(master=notebook)


notebook.add(child=linear_tab, text="Target Linear Motion")
notebook.add(child=rotation_tab, text="Substrate Rotation")
notebook.add(child=mirror_tab, text="Mirror Planar Motion")
notebook.add(child=serial_tab, text="Serial Connection")

try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
