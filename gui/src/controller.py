import tkinter as tk
from functools import partial
from queue import Queue
from tkinter import Widget, ttk
from typing import cast

from gui.src.model import Model
from gui.src.serial_threads import SerialWorker
from gui.src.view import LinearTab, RotationTab, View
from gui.src.widgets import SendButton, UnitsCombobox


class Controller(ttk.Frame):
    def __init__(self, master: tk.Misc, view: View, model: Model) -> None:
        super().__init__(master=master)

        self.inbox: Queue[str] = Queue[str](maxsize=32)
        self.outbox: Queue[str] = Queue[str](maxsize=32)
        self.thread: SerialWorker = SerialWorker(
            inbox=self.inbox, outbox=self.outbox, model=model
        )

        self.model: Model = Model(queue=self.outbox)
        self.view: View = View(master=self)
        self.thread.start()

        self._bind_linear_tab()
        self._bind_rotation_tab()

    def _bind_linear_tab(self) -> None:
        lin_tab: LinearTab = self.view.linear_tab
        components: dict[str, dict[str, Widget]] = lin_tab.param_frame.components

        def get_btn(name: str) -> SendButton:
            return cast(SendButton, components[name]["button"])

        def get_units(name: str) -> UnitsCombobox:
            return cast(UnitsCombobox, components[name]["units"])

        ################################################
        # Parameters
        ################################################
        get_btn(name="max_speed").bind_callback(
            callback=partial[None](
                self.handle_parameter, "s2", "max", get_units(name="max_speed")
            )
        )
        get_btn(name="acceleration").bind_callback(
            callback=partial[None](
                self.handle_parameter, "s2", "acc", get_units(name="acceleration")
            )
        )

        ################################################
        # Movements
        ################################################
        get_btn(name="final_position").bind_callback(
            callback=partial[None](
                self.handle_movement, "s2", "end", get_units(name="final_position")
            )
        )
        get_btn(name="abs_mov").bind_callback(
            callback=partial[None](
                self.handle_movement, "s2", "mtp", get_units(name="abs_mov")
            )
        )
        get_btn(name="rel_mov").bind_callback(
            callback=partial[None](
                self.handle_movement, "s2", "mov", get_units(name="rel_mov")
            )
        )

        ################################################
        # Booleans
        ################################################
        lin_tab.dir_rad.bind_callback(
            callback=partial[None](self.handle_direction, "s2")
        )
        lin_tab.toggle_button.bind_callback(
            callback=partial[None](self.handle_toggle, "s2")
        )

        ################################################
        # Actions
        ################################################
        lin_tab.set_home_button.bind_callback(callback=self.model.s2_set_home)
        lin_tab.go_home_button.bind_callback(callback=self.model.s2_go_home)

    def _bind_rotation_tab(self) -> None:
        rot_tab: RotationTab = self.view.rotation_tab
        components: dict[str, dict[str, Widget]] = rot_tab.param_frame.components

        def get_btn(name: str) -> SendButton:
            return cast(SendButton, components[name]["button"])

        def get_units(name: str) -> UnitsCombobox:
            return cast(UnitsCombobox, components[name]["units"])

        ################################################
        # Parameters
        ################################################
        get_btn(name="max_speed").bind_callback(
            callback=partial[None](
                self.handle_parameter, "s1", "max", get_units(name="max_speed")
            )
        )
        get_btn(name="speed").bind_callback(
            callback=partial[None](
                self.handle_parameter, "s1", "spd", get_units(name="speed")
            )
        )

        ################################################
        # Booleans
        ################################################
        rot_tab.dir_rad.bind_callback(
            callback=partial[None](self.handle_direction, "s1")
        )
        rot_tab.toggle_button.bind_callback(
            callback=partial[None](self.handle_toggle, "s1")
        )

    ################################################
    # Handlers
    ################################################
    def handle_parameter(
        self, motor: str, attr_name: str, unit_widget: UnitsCombobox, value_str: str
    ) -> None:
        try:
            raw_value: float = float(value_str)
        except ValueError:
            return

        unit: str = unit_widget.selected_unit.get()
        conv_factor: float = self.model.unit_conversions[motor].get(unit, 1.0)

        dir_mult: int = cast(int, getattr(self.model, f"{motor}_dir"))

        final_value: float = raw_value * conv_factor * dir_mult
        self._route_value(motor, attr_name, final_value)

    def handle_movement(
        self, motor: str, attr_name: str, unit_widget: UnitsCombobox, value_str: str
    ) -> None:
        try:
            raw_value: float = float(value_str)
        except ValueError:
            return

        unit: str = unit_widget.selected_unit.get()
        conv_factor: float = self.model.unit_conversions[motor].get(unit, 1.0)

        final_value: float = raw_value * conv_factor

        if attr_name in ["end", "mov", "mtp", "mta"]:
            final_int: int = int(final_value)
            self._route_value(motor, attr_name, final_value=final_int)
        else:
            self._route_value(motor, attr_name, final_value)

    def handle_direction(self, motor: str, direction: int) -> None:
        setattr(self.model, f"{motor}_dir", direction)

    def handle_toggle(self, motor: str, is_on: bool) -> None:
        setattr(self.model, f"{motor}_is_on", is_on)

        if is_on:
            if motor == "s1":
                attrs: list[str] = ["max", "spd"]
            else:
                attrs = ["max", "acc", "end", "mov", "mtp", "mta"]

            for attr in attrs:
                stgd_val: float | int = cast(
                    float | int, getattr(self.model, f"stgd_{motor}_{attr}")
                )
                setattr(self.model, f"{motor}_{attr}", stgd_val)

    def _route_value(
        self, motor: str, attr_name: str, final_value: float | int
    ) -> None:
        is_on: bool = cast(bool, getattr(self.model, f"{motor}_is_on"))

        if is_on:
            setattr(self.model, f"{motor}_{attr_name}", final_value)
        else:
            setattr(self.model, f"stgd_{motor}_{attr_name}", final_value)
