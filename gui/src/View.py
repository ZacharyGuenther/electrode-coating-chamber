import tkinter as tk
from tkinter import ttk

from gui.src.widgets import (
    BoolRadios,
    CustomEntry,
    OnOffButton,
    SendButton,
    UnitsCombobox,
    setup_styles,
)


################################################
# Tab Builder
################################################
class TabBuilder(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.components: dict[str, dict[str, tk.Widget]] = {}

        _ = self.columnconfigure(index=0, uniform="column0", minsize=110)
        _ = self.columnconfigure(index=1, uniform="column1")
        _ = self.columnconfigure(index=2, uniform="column2")
        _ = self.columnconfigure(index=3, uniform="column3")

    def create(self, widget_data: list[dict[str, str]]) -> None:
        padx: int = 3
        pady: int = 10
        for row_index, config in enumerate[dict[str, str]](widget_data):
            name: str = config["name"]
            unit_type: str = config["type"]
            label_text: str = config["text"]

            label: ttk.Label = ttk.Label(master=self, text=label_text, anchor="center")
            label.grid(column=0, row=row_index, sticky="nsew", padx=padx, pady=pady)

            entry: CustomEntry = CustomEntry(master=self)
            entry.grid(column=1, row=row_index, sticky="nsew", padx=padx, pady=pady)

            combobox: UnitsCombobox = UnitsCombobox(master=self, unit_type=unit_type)
            combobox.grid(column=2, row=row_index, sticky="nsew", padx=padx, pady=pady)

            button: SendButton = SendButton(master=self)
            button.grid(column=3, row=row_index, sticky="ew", padx=padx, pady=pady)
            button.bind_companion(companion=entry)

            self.components[name] = {
                "label": label,
                "entry": entry,
                "units": combobox,
                "button": button,
            }


################################################
# Notebook Tabs
################################################
class LinearTab(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        param_config: list[dict[str, str]] = [
            {"name": "max_speed", "text": "Max Speed:", "type": "speed"},
            {"name": "acceleration", "text": "Acceleration:", "type": "accel"},
            {"name": "final_position", "text": "Final Position:", "type": "position"},
            {"name": "abs_mov", "text": "Move to:", "type": "position"},
            {"name": "rel_mov", "text": "Move:", "type": "position"},
        ]

        self.param_frame: TabBuilder = TabBuilder(master=self)
        self.param_frame.create(widget_data=param_config)
        self.param_frame.pack(expand=True)

        self.dir_rad: BoolRadios = BoolRadios(
            master=self.param_frame,
            left_text="Into Chamber",
            right_text="Out of Chamber",
        )
        self.dir_rad.grid(row=5, column=1, columnspan=2)

        self.param_frame.components["rel_mov"]["label"].grid(
            row=4, column=0, rowspan=2, sticky="ew", padx=5, pady=10
        )
        self.param_frame.components["rel_mov"]["button"].grid(
            row=4, column=3, rowspan=2, sticky="ew", padx=5, pady=10
        )

        self.state_frame: ttk.Frame = ttk.Frame(master=self)
        self.state_frame.pack(side="bottom", pady=30)

        self.set_home_button: SendButton = SendButton(
            master=self.state_frame, text="Set Home"
        )
        self.set_home_button.pack(side="left", padx=10)

        self.go_home_button: SendButton = SendButton(
            master=self.state_frame, text="Go Home"
        )
        self.go_home_button.pack(side="left", padx=10)

        self.toggle_button: OnOffButton = OnOffButton(master=self.state_frame)
        self.toggle_button.pack(side="left", padx=10)


class RotationTab(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        param_config: list[dict[str, str]] = [
            {"name": "max_speed", "text": "Max Speed:", "type": "speed"},
            {"name": "speed", "text": "Speed:", "type": "speed"},
        ]

        self.param_frame: TabBuilder = TabBuilder(master=self)
        self.param_frame.create(widget_data=param_config)
        self.param_frame.pack(expand=True)

        self.dir_rad: BoolRadios = BoolRadios(
            master=self.param_frame, left_text="\u03c9 > 0", right_text="\u03c9 < 0"
        )
        self.dir_rad.grid(row=2, column=1, columnspan=2)

        self.toggle_button: OnOffButton = OnOffButton(master=self.param_frame)
        self.toggle_button.grid(column=1, columnspan=2, row=3, pady=50)


class MirrorTab(ttk.Frame):
    pass


class SerialTab(ttk.Frame):
    pass


################################################
# Main App
################################################
class App(ttk.Notebook):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)
        self.pack(fill="both", expand=True)

        setup_styles(master=master)

        self.linear_tab: LinearTab = LinearTab(master=self)
        self.add(child=self.linear_tab, text="Target Linear Motion")

        self.rotation_tab: RotationTab = RotationTab(master=self)
        self.add(child=self.rotation_tab, text="Substrate Rotation")
