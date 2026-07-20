import tkinter as tk
from tkinter import Widget, ttk

from gui.src.widgets import (
    BoolRadios,
    CustomEntry,
    OnOffButton,
    SendButton,
    UnitsCombobox,
    bind_highlight_on_focus,
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
            button.bind_companion(companion=entry, units=combobox)

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
            {"name": "max", "text": "Max Speed:", "type": "speed"},
            {"name": "acc", "text": "Acceleration:", "type": "accel"},
            {"name": "end", "text": "Final Position:", "type": "position"},
            {"name": "mtp", "text": "Move to:", "type": "position"},
            {"name": "mov", "text": "Move:", "type": "position"},
        ]

        self.param_frame: TabBuilder = TabBuilder(master=self)
        self.param_frame.create(widget_data=param_config)
        self.param_frame.pack(expand=True)

        temp_widgets: dict[str, Widget] = self.param_frame.components["mtp"]
        for widget in temp_widgets.values():
            widget.grid(pady=(30, 10))

        self.dir_rad: BoolRadios = BoolRadios(
            master=self.param_frame,
            left_text="Into Chamber",
            right_text="Out of Chamber",
        )
        self.dir_rad.grid(row=5, column=1, columnspan=2)

        # self.param_frame.components["rel_mov"]["label"].grid(
        #    row=4, column=0, rowspan=2, sticky="ew", padx=5, pady=10
        # )
        # self.param_frame.components["rel_mov"]["button"].grid(
        #    row=4, column=3, rowspan=2, sticky="ew", padx=5, pady=10
        # )

        self.state_frame: ttk.Frame = ttk.Frame(master=self)
        self.state_frame.pack(side="bottom", pady=25)

        self.set_button: SendButton = SendButton(
            master=self.state_frame, text="Set Home"
        )
        self.set_button.pack(side="left", padx=10)

        self.hom_button: SendButton = SendButton(
            master=self.state_frame, text="Go Home"
        )
        self.hom_button.pack(side="left", padx=10)

        self.toggle_button: OnOffButton = OnOffButton(master=self.state_frame)
        self.toggle_button.pack(side="left", padx=10)


class RotationTab(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        param_config: list[dict[str, str]] = [
            {"name": "max", "text": "Max Speed:", "type": "speed"},
            {"name": "spd", "text": "Speed:", "type": "speed"},
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
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        _ = self.columnconfigure((0, 1, 2, 3), weight=1)

        self.mp1_label: ttk.Label = ttk.Label(master=self, text="Microprocessor 1:")
        self.mp1_label.grid(row=0, column=0, sticky="e", padx=5, pady=(30, 10))

        self.ports: list[str] = ["No USB ports available!"]
        self.selected_port: tk.StringVar = tk.StringVar(value=self.ports[0])
        self.port_options: ttk.Combobox = ttk.Combobox(
            master=self, textvariable=self.selected_port, state="normal"
        )
        self.port_options.grid(row=0, column=1, sticky="ew", padx=5, pady=(30, 10))
        bind_highlight_on_focus(widget=self.port_options)

        self.connect_btn: SendButton = SendButton(master=self, text="Connect")
        self.connect_btn.grid(row=0, column=2, sticky="w", padx=5, pady=(30, 10))

        self.connect_btn.bind_companion(companion=self.port_options)


################################################
# Main App
################################################
class View(ttk.Notebook):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)
        self.pack(fill="both", expand=True)

        setup_styles(master=master)

        self.linear_tab: LinearTab = LinearTab(master=self)
        self.add(child=self.linear_tab, text="Target Linear Motion")

        self.rotation_tab: RotationTab = RotationTab(master=self)
        self.add(child=self.rotation_tab, text="Substrate Rotation")

        self.serial_tab: SerialTab = SerialTab(master=self)
        self.add(child=self.serial_tab, text="Serial Interface")
