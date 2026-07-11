import tkinter as tk

from gui.src.View import App

if __name__ == "__main__":
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

    view: App = App(master=root)

    root.mainloop()
