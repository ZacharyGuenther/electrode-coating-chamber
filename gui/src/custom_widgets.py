import tkinter as tk
from tkinter import ttk
from typing import Literal

# BASE COMPONENTS

class BaseFlashButton(ttk.Button):
  
    _timer_id: str | None
    _delay_ms: int

    def __init__(self, master: tk.Misc, flash_timer: int = 1250, **kwargs: object) -> None:
        
        user_command: object = kwargs.pop("command", None)
        
        super().__init__(master=master, style="Custom.TButton", **kwargs)  # pyright: ignore[reportArgumentType]
        
        self._timer_id = None
        self._delay_ms = flash_timer
        self._setup_styles()
        
        _ = self.configure(command=lambda: self._handle_click(user_command))

    def _setup_styles(self) -> None:
        style: ttk.Style = ttk.Style()
        style.theme_use("alt")
        
        style.configure("Custom.TButton", background="darkred", foreground="white")
        _ = style.map("Custom.TButton", background=[("active", "red")])

        style.configure("Success.TButton", background="green", foreground="white")
        _ = style.map("Success.TButton", background=[("active", "green")], foreground=[("active", "white")])

    def _handle_click(self, user_command: object) -> None:
        if self._timer_id:
            self.after_cancel(id=self._timer_id)
            
        
        if callable(user_command):
            result: object = user_command()

            if result == "invalid":
                return

        _ = self.configure(style="Success.TButton")    
        self._timer_id = self.after(ms=self._delay_ms, func=self._reset_style)

    def _reset_style(self) -> None:
        _ = self.configure(style="Custom.TButton")
        self._timer_id = None


class BaseToggleButton(ttk.Button):

    off_text: str
    on_text: str
    _is_off: bool
    _timer_id: str | None
    _delay_ms: int

    def __init__(self, master: tk.Misc, off_text: str, on_text: str, **kwargs: object) -> None:

        user_command: object = kwargs.pop("command", None)
        
        super().__init__(master=master, text=off_text, style="off.TButton", **kwargs)  # pyright: ignore[reportArgumentType]
        
        self.off_text = off_text
        self.on_text = on_text
        self._is_off = True
        self._timer_id = None
        self._delay_ms = 1250
        self._setup_styles()
        
        _ = self.configure(command=lambda: self._handle_toggle(user_command))

    def _setup_styles(self) -> None:
        style: ttk.Style = ttk.Style()
        style.theme_use("alt")
       
        style.configure("off.TButton", background="darkred", foreground="white")
        _ = style.map("off.TButton", background=[("active", "red")])

        style.configure("on.TButton", background="green", foreground="white")
        _ = style.map("on.TButton", background=[("active", "green")], foreground=[("active", "white")])

        style.configure("onDelay.TButton", background="green", foreground="white")
        _ = style.map("onDelay.TButton", background=[("active", "darkgreen")], foreground=[("active", "white")])

    def _handle_toggle(self, user_command: object) -> None:
        if self._timer_id:
            self.after_cancel(self._timer_id)

        if self._is_off:
            _ = self.configure(style="on.TButton", text=self.on_text)
            self._timer_id = self.after(ms=self._delay_ms, func=self._settle_on_style)
        else:
            _ = self.configure(style="off.TButton", text=self.off_text)
            
        self._is_off = not self._is_off

        if callable(user_command):
            _ = user_command(not self._is_off)

    def _settle_on_style(self) -> None:
        _ = self.configure(style="onDelay.TButton", text=self.on_text)
        self._timer_id = None


# COMPOSITE WIDGETS

class LabelEntryButton(tk.Frame):
  
    label: ttk.Label
    entry: ttk.Entry
    button: BaseFlashButton
    value: float

    def __init__(self, parent: tk.Misc, label_text: str, button_text: str, **kwargs: object) -> None:
        super().__init__(master=parent, **kwargs)  # pyright: ignore[reportArgumentType]
        self.value = 0.0

        self.label = ttk.Label(master=self, text=label_text)
        self.label.grid(column=1, row=1, padx=5)

        self.entry = ttk.Entry(master=self)
        self.entry.grid(column=2, row=1, padx=5)
        _ = self.entry.bind("<FocusIn>", self._select_all)

        self.button = BaseFlashButton(
            master=self,
            text=button_text,
            command=self._pull_entry_data
        )
        self.button.grid(column=3, row=1)

    def _select_all(self, _event: tk.Event) -> str:
        self.entry.selection_range(start=0, end="end")
        return "break"

    def _pull_entry_data(self) -> None | Literal["invalid"]:
        raw_entry_data: str = self.entry.get()
        try:
            self.value = float(raw_entry_data)
            return None

        except ValueError:
            self.entry.delete(first=0, last="end")
            self.entry.insert(index=0, string="Invalid number!")
            return "invalid"


class OnOffToggleNum(BaseToggleButton):

    def __init__(self, master: tk.Misc, **kwargs: object) -> None:
        super().__init__(master=master, off_text='Off', on_text='On', **kwargs)


class BooleanRadios(tk.Frame):
    
    dir_multiplier: tk.IntVar
    left_radio: ttk.Radiobutton
    left_text: str
    right_radio: ttk.Radiobutton
    right_text: str


    def __init__(self, parent: tk.Misc, left_text: str, right_text: str, **kwargs: object) -> None:
        super().__init__(master=parent, **kwargs)  # pyright: ignore[reportArgumentType]

        self.left_text = left_text
        self.right_text = right_text
        self.dir_multiplier = tk.IntVar(value=1)

        self.left_radio = ttk.Radiobutton(
            master=self, text=self.left_text, value=1, variable=self.dir_multiplier
        )
        self.left_radio.grid(column=1, row=1)

        self.right_radio = ttk.Radiobutton(
            master=self, text=self.right_text, value=-1, variable=self.dir_multiplier
        )
        self.right_radio.grid(column=2, row=1, padx=5) 
