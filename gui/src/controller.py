import tkinter as tk
from functools import partial
from queue import Queue
from tkinter import Widget, ttk
from typing import cast

from gui.src.model import Model, StepperMotor
from gui.src.serial_threads import SerialWorker
from gui.src.view import View
from gui.src.widgets import BoolRadios, OnOffButton, SendButton


class Controller(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master=master)

        self.inbox: Queue[str] = Queue[str](maxsize=32)
        self.outbox: Queue[str] = Queue[str](maxsize=32)

        self.model: Model = Model(queue=self.outbox)
        self.model.bind_port_update(callback=self._on_ports_updated)

        self.allowed_motors: list[str] = ["s1", "s2"]

        self.view: View = View(master=self)
        self.bind_linear_tab()
        self.bind_rotation_tab()
        self.bind_serial_tab()

        self.thread: SerialWorker = SerialWorker(
            inbox=self.inbox, outbox=self.outbox, model=self.model
        )
        self.thread.start()

    def _route_value(
        self, motor: StepperMotor, attr_name: str, final_value: float | int
    ) -> None:
        if motor.is_on:
            setattr(motor, attr_name, final_value)
        else:
            setattr(motor, f"stgd_{attr_name}", final_value)

    def radio_callback(self, motor: str, dir_multiplier: int) -> None:
        if motor in self.allowed_motors:
            target_motor: StepperMotor = cast(StepperMotor, getattr(self.model, motor))
            target_motor.dir = dir_multiplier
        else:
            raise ValueError(
                f"The selection motor='{motor}' is not allowed. "
                + f"Choose one of {self.allowed_motors}."
            )

    def _send_parameter(
        self,
        parameter: str,
        motor: str,
        value: str,
        selected_unit: str,
        value_type: type[float] | type[int],
    ) -> None:
        if motor not in self.allowed_motors:
            print(f"Error: Motor '{motor}' not allowed.")
            return

        try:
            target_motor: StepperMotor = cast(StepperMotor, getattr(self.model, motor))
            conv_factor: float = target_motor.conv_factors.get(selected_unit, 1.0)
            dir_multiplier: int = 1

            combo: str = f"{motor.lower()}.{parameter.lower()}"
            if combo == "s2.mov" or combo == "s1.spd":
                dir_multiplier = target_motor.dir

            raw_value: float = float(value) * conv_factor * dir_multiplier
            final_value: float | int = value_type(raw_value)

            self._route_value(
                motor=target_motor, attr_name=parameter.lower(), final_value=final_value
            )

        except (ValueError, AttributeError) as e:
            print(f"Invalid input for {motor}.{parameter}: {e}")

    def on_off_callback(self, motor: str, is_on: bool) -> None:
        if motor in self.allowed_motors:
            target_motor: StepperMotor = cast(StepperMotor, getattr(self.model, motor))
            target_motor.is_on = is_on
            if is_on:
                parameters: list[str] = [
                    "max",
                    "spd",
                    "acc",
                    "end",
                    "mov",
                    "mtp",
                    "mta",
                ]

                for param in parameters:
                    staged_val: float | int | None = getattr(  # pyright: ignore[reportAny]
                        target_motor, f"stgd_{param}"
                    )
                    if staged_val is not None:
                        setattr(target_motor, param, staged_val)
                        setattr(target_motor, f"stgd_{param}", None)

    def _bind_components(
        self, motor: str, components: dict[str, dict[str, Widget]]
    ) -> None:
        for name, comp_dict in components.items():
            button: SendButton = cast(SendButton, comp_dict["button"])

            value_type: type[float] | type[int]
            if name in ["max", "spd", "acc"]:
                value_type = float
            else:
                value_type = int

            button.bind_callback(
                callback=partial(
                    self._send_parameter, name, motor, value_type=value_type
                )
            )

    def bind_linear_tab(self) -> None:
        components: dict[str, dict[str, Widget]] = (
            self.view.linear_tab.param_frame.components
        )
        self._bind_components(motor="s2", components=components)

        dir_rad: BoolRadios = self.view.linear_tab.dir_rad
        dir_rad.bind_callback(callback=partial(self.radio_callback, "s2"))

        set_btn: SendButton = self.view.linear_tab.set_button
        set_btn.bind_callback(callback=self.model.s2.set_home)

        hom_btn: SendButton = self.view.linear_tab.hom_button
        hom_btn.bind_callback(callback=self.model.s2.go_home)

        is_on_btn: OnOffButton = self.view.linear_tab.toggle_button
        is_on_btn.bind_callback(callback=partial(self.on_off_callback, "s2"))

        stop_btn: SendButton = self.view.linear_tab.stop_button
        stop_btn.bind_callback(callback=self.model.s2.reset_board)

    def bind_rotation_tab(self) -> None:
        components: dict[str, dict[str, Widget]] = (
            self.view.rotation_tab.param_frame.components
        )
        self._bind_components(motor="s1", components=components)

        dir_rad: BoolRadios = self.view.rotation_tab.dir_rad
        dir_rad.bind_callback(callback=partial(self.radio_callback, "s1"))

        is_on_btn: OnOffButton = self.view.rotation_tab.toggle_button
        is_on_btn.bind_callback(callback=partial(self.on_off_callback, "s1"))

        stop_btn: SendButton = self.view.rotation_tab.stop_button
        stop_btn.bind_callback(callback=self.model.s1.reset_board)

    def bind_serial_tab(self) -> None:
        connect_btn: SendButton = self.view.serial_tab.connect_btn
        connect_btn.bind_callback(callback=self.handle_connect)

    def _on_ports_updated(self, ports: list[str]) -> None:
        def update() -> None:
            safe_ports: list[str] = ports if ports else ["No USB ports available!"]
            _ = self.view.serial_tab.port_options.configure(values=safe_ports)

            current_selection: str = self.view.serial_tab.selected_port.get()
            if current_selection not in safe_ports:
                self.view.serial_tab.selected_port.set(value=safe_ports[0])

        _ = self.after(ms=0, func=update)

    def handle_connect(self) -> None:
        selection: str = self.view.serial_tab.selected_port.get()

        if not selection or selection == "No USB ports available!":
            return

        if self.thread.is_connected():
            self.thread.disconnect()
            print("Disconnected from serial port.")
            return

        error: str | None = self.thread.connect(
            port=selection, baudrate=115200, timeout=0.05
        )
        if error is None:
            print(f"Connected to {selection}")
        else:
            print(f"Failed to connect to {selection}: {error}")
