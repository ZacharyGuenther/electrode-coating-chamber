import tkinter as tk

from gui.src.controller import Controller

root: tk.Tk = tk.Tk()
root.title("Electrode Chamber Control Interface")

# Center GUI
window_width = 640
window_height = 500

screen_width: int = root.winfo_screenwidth()
screen_height: int = root.winfo_screenheight()

center_x: int = int(screen_width / 2 - window_width / 2)
center_y: int = int(screen_height / 2 - window_height / 2)

root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

app: Controller = Controller(master=root)
app.pack(fill="both", expand=True)

if __name__ == "__main__":
    root.mainloop()
