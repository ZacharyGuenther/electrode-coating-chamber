import tkinter as tk
from tkinter import ttk

class LabelEntryButton(tk.Frame):
    label: ttk.Label
    entry: ttk.Entry
    button: ttk.Button
    value: float
    style: ttk.Style
    _timer_id: str | None
    _delay_ms: int

    def __init__(self, parent: tk.Misc, label_text: str, button_text:str, **kwargs: object) -> None:
        super().__init__(master=parent, **kwargs)   # pyright: ignore[reportArgumentType]

        self.label = ttk.Label(master=self, text=label_text) 
        self.label.grid(column=1, row=1, padx=5)

        self.entry = ttk.Entry(master=self)
        self.entry.grid(column=2, row=1, padx=5)
        
        self.button = ttk.Button(master=self, text=button_text, style="Custom.TButton", command=self._pull_entry_data)
        self.button.grid(column=3, row=1)

        _ = self.entry.bind('<FocusIn>', self._select_all)

        self.value = 0.0
        self._timer_id = None
        self._delay_ms = 1750

        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure(
            'Custom.TButton',
            background='darkred',
            foreground='white',
        )
        _ = self.style.map(
            "Custom.TButton",
            background=[('active', 'red')]
        )

        self.style.configure(
            'Success.TButton',
            background='green',
            foreground='white'
        )
        _ = self.style.map(
            'Success.TButton',
            background=[('active', 'green')],
            foreground=[('active', 'white')]
            )

    def _select_all(self, _event: tk.Event):
        self.entry.selection_range(0, 'end')
        return 'break'    

    def _reset_button_style(self) -> None:
        _ = self.button.configure(style='Custom.TButton')
        self._timer_id = None

    def _pull_entry_data(self) -> None:
        raw_entry_data: str = self.entry.get()

        try:
            self.value = float(raw_entry_data)
            
            if self._timer_id:
                self.after_cancel(id=self._timer_id)
        
            _ = self.button.config(style='Success.TButton')

            self._timer_id = self.after(ms=self._delay_ms , func=self._reset_button_style)
        
        except ValueError:
            self.entry.delete(first=0, last='end')
            self.entry.insert(index=0, string='Invalid number!')

class OnOffToggleNum(ttk.Button):
    style: ttk.Style
    _is_off: bool
    _timer_id: str | None
    _delay_ms: int

    def __init__(self, master: tk.Misc, **kwargs: object) ->None:
        
        _ = kwargs.setdefault('text', 'Off')
        _ = kwargs.setdefault('style', 'off.TButton')
        _ = kwargs.setdefault('command', self._toggle_numerical)
        
        super().__init__(master=master, **kwargs)   # pyright: ignore[reportArgumentType]

        self._is_off = True
        self._timer_id = None
        self._delay_ms = 1250

        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure(
            'off.TButton',
            background='darkred',
            foreground='white',
        )
        _ = self.style.map(
            "off.TButton",
            background=[('active', 'red')]
        )

        self.style.configure(
            'on.TButton',
            background='green',
            foreground='white'
        )

        _ = self.style.map(
            'on.TButton',
            background=[('active', 'green')],
            foreground=[('active', 'white')]
            )  

        self.style.configure(
            'onDelay.TButton',
            background='green',
            foreground='white'
        )
        _ = self.style.map(
            'onDelay.TButton',
            background=[('active', 'darkgreen')],
            foreground=[('active', 'white')]
            )    
    
    def _delay_on_style(self) -> None:
        _ = self.configure(style='onDelay.TButton', text='On')
        self._timer_id = None

    def _toggle_numerical(self) ->None:
        
        if self._is_off:
            _ = self.configure(style='on.TButton', text='On')

            if self._timer_id:
                self.after_cancel(id=self._timer_id)

            self._timer_id = self.after(ms=self._delay_ms, func=self._delay_on_style)

            ### Add the logic for the actually arduino serial section

        else:
            if self._timer_id:
                self.after_cancel(id=self._timer_id)

            _ = self.configure(style='off.TButton', text='Off')
        
        self._is_off = not self._is_off

# class 