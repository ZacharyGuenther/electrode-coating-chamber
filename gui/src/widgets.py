import tkinter as tk
from tkinter import ttk
from typing import Callable


################################################
# Global Styling
################################################
def setup_styles(master: tk.Misc) -> None:
    style: ttk.Style = ttk.Style()
    style.theme_use("alt")

    bg: str = "grey12"
    ent_bg: str = "grey35"
    frm_bg: str = "grey12"
    base_btn_bg: str = "darkred"
    on_btn_bg: str = "green"
    base_btn_act: str = "red"
    on_btn_act: str = "darkgreen"
    lstbx_bg: str = "grey45"

    text: str = "grey90"
    font: str = "Arial"
    brdr_sty: str = "thin"

    master["bg"] = frm_bg

    style.configure("TRadiobutton", background=frm_bg, foreground=text, font=font)
    _ = style.map(
        "TRadiobutton",
        background=[("active", frm_bg), ("pressed", frm_bg)],
        indicatorcolor=[("selected", text), ("!selected", ent_bg)],
    )

    style.configure("TNotebook.Tab", background=bg, foreground=text, font=font)

    _ = style.map(
        "TNotebook.Tab", background=[("selected", ent_bg), ("active", lstbx_bg)]
    )

    style.configure("TNotebook", background=frm_bg, text=text, font=font)

    style.configure("TFrame", background=frm_bg)

    style.configure("TLabel", background=bg, foreground=text, font=font)

    style.configure(
        "TEntry",
        fieldbackground=ent_bg,
        foreground=text,
        font=font,
        bordercolor=ent_bg,
        insertcolor=text,
    )

    style.configure("TButton", background=base_btn_bg, foreground=text, font=font)
    _ = style.map("TButton", background=[("active", base_btn_act)])

    style.configure("Send.TButton", background=on_btn_bg, foreground=text)
    _ = style.map("Send.TButton", background=[("active", on_btn_bg)])

    style.configure("On.TButton", background=on_btn_bg, foreground=text)
    _ = style.map("On.TButton", background=[("active", on_btn_act)])

    style.configure(
        "TCombobox",
        background=bg,
        foreground=text,
        arrowcolor=text,
        relief=brdr_sty,
        bordercolor=ent_bg,
        font=font,
    )
    _ = style.map(
        "TCombobox",
        background=[("active", ent_bg)],
        fieldbackground=[("readonly", bg)],
        selectbackground=[("focus", frm_bg), ("readonly", frm_bg)],
        selectforeground=[("focus", text), ("readonly", text)],
    )

    combobox_listbox_options: dict[str, str] = {
        "*TCombobox*Listbox*background": ent_bg,
        "*TCombobox*Listbox*foreground": text,
        "*TCombobox*Listbox*selectBackground": lstbx_bg,
        "*TCombobox*Listbox*selectForeground": text,
    }
    for pattern, value in combobox_listbox_options.items():
        master.option_add(pattern, value)  # pyright: ignore[reportUnknownMemberType]


################################################
# Custom Widgets
################################################
class SendButton(ttk.Button):
    def __init__(
        self, master: tk.Misc, text: str = "Send", delay_ms: int = 1250
    ) -> None:
        super().__init__(master=master, command=self._on_click, text=text)

        self._delay_ms: int = delay_ms
        self._timer_id: str | None = None
        self._callback: Callable[[str], None] | None = None
        self._companion: ttk.Entry | None = None

    def _on_click(self) -> None:
        if self._timer_id:
            self.after_cancel(id=self._timer_id)

        _ = self.configure(style="Send.TButton")
        self._timer_id = self.after(
            ms=self._delay_ms, func=lambda: self.configure(style="TButton")
        )

        if self._callback and self._companion:
            self._callback(self._companion.get())

    def bind_companion(self, companion: ttk.Entry) -> None:
        self._companion = companion

    def bind_callback(self, callback: Callable[[str], None]) -> None:
        self._callback = callback


class OnOffButton(ttk.Button):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master, command=self._on_click, text="Off")

        self._is_on: tk.BooleanVar = tk.BooleanVar(value=False)
        self._callback: Callable[[bool], None] | None = None

    def _on_click(self) -> None:

        if self._is_on.get():
            _ = self.configure(text="Off", style="TButton")
            self._is_on.set(value=False)
        else:
            _ = self.configure(text="On", style="On.TButton")
            self._is_on.set(value=True)

        if self._callback:
            self._callback(self._is_on.get())

    def bind_callback(self, callback: Callable[[bool], None]) -> None:
        self._callback = callback


class UnitsCombobox(ttk.Combobox):
    def __init__(self, master: tk.Misc, unit_type: str = "position") -> None:

        self.unit_type: str = unit_type

        if self.unit_type == "position":
            self.units: list[str] = ["mm", "cm", "step"]
        elif self.unit_type == "speed":
            self.units = ["RPM", "step/s"]
        elif self.unit_type == "accel":
            self.units = ["RPM/s", "step/s\u00b2"]
        else:
            raise ValueError(
                f"Invalid unit_type '{self.unit_type}'. "
                + "Choose 'position', 'speed', or 'accel'."
            )

        self.selected_unit: tk.StringVar = tk.StringVar(value=self.units[0])

        super().__init__(
            master=master,
            state="readonly",
            justify="center",
            width=6,
            textvariable=self.selected_unit,
            values=self.units,
        )

        self._callback: Callable[[str], None] | None = None
        _ = self.bind("<<ComboboxSelected>>", self._on_click)

    def _on_click(self, _event: tk.Event) -> None:
        if self._callback:
            self._callback(self.selected_unit.get())

    def bind_callback(self, callback: Callable[[str], None]) -> None:
        self._callback = callback


class BoolRadios(ttk.Frame):
    def __init__(self, master: tk.Misc, left_text: str, right_text: str) -> None:
        super().__init__(master=master)

        self.dir_multiplier: tk.IntVar = tk.IntVar(value=1)
        self._callback: Callable[[int], None] | None = None

        self.lrad: ttk.Radiobutton = ttk.Radiobutton(
            master=self,
            command=self._on_click,
            text=left_text,
            value=1,
            variable=self.dir_multiplier,
        )
        self.lrad.grid(column=0, row=0, padx=10)

        self.rrad: ttk.Radiobutton = ttk.Radiobutton(
            master=self,
            command=self._on_click,
            text=right_text,
            value=-1,
            variable=self.dir_multiplier,
        )
        self.rrad.grid(column=1, row=0, padx=10)

    def _on_click(self) -> None:
        if self._callback:
            self._callback(self.dir_multiplier.get())

    def bind_callback(self, callback: Callable[[int], None]) -> None:
        self._callback = callback


class CustomEntry(ttk.Entry):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self._callback: Callable[..., None] | None = None

    def on_focus(self) -> None:
        if self._callback:
            _ = self.bind("<FocusIn>", self._callback)

    def bind_callback(self, callback: Callable[..., None]) -> None:
        self._callback = callback
