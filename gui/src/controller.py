import tkinter as tk
from functools import partial
from queue import Queue
from tkinter import Widget, ttk
from typing import Callable, cast

import serial
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

        self.view: View = View(master=self)
        self.bind_linear_tab()
        self.bind_rotation_tab()
        self.bind_serial_tab()

        self.thread: SerialWorker = SerialWorker(
            inbox=self.inbox, outbox=self.outbox, model=self.model
        )
        self.thread.start()

        self.allowed_motors: list[str] = ["s1", "s2"]

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

    def send_spd_acc(
        self, parameter: str, motor: str, value: str, selected_unit: str
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

            final_value: float = float(value) * conv_factor * dir_multiplier
            self._route_value(
                motor=target_motor, attr_name=parameter.lower(), final_value=final_value
            )

        except (ValueError, AttributeError) as e:
            print(f"Invalid input or parameter: {e}")

    def send_pos(
        self, parameter: str, motor: str, value: str, selected_unit: str
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

            final_value: int = int(float(value) * conv_factor * dir_multiplier)
            self._route_value(
                motor=target_motor, attr_name=parameter.lower(), final_value=final_value
            )

        except (ValueError, AttributeError) as e:
            print(f"Invalid input or parameter: {e}")

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
                    staged_val: float = cast(
                        float, getattr(target_motor, f"stgd_{param}")
                    )
                    if staged_val != 0:
                        setattr(target_motor, param, staged_val)

    def _bind_components(
        self, motor: str, components: dict[str, dict[str, Widget]]
    ) -> None:
        for name, comp_dict in components.items():
            button: SendButton = cast(SendButton, comp_dict["button"])

            target_func: Callable[..., None]
            if name in ["max", "spd", "acc"]:
                target_func = self.send_spd_acc
            else:
                target_func = self.send_pos

            button.bind_callback(
                callback=partial(target_func, parameter=name, motor=motor)
            )

    def bind_linear_tab(self) -> None:
        components: dict[str, dict[str, Widget]] = (
            self.view.linear_tab.param_frame.components
        )
        self._bind_components(motor="s2", components=components)

        dir_rad: BoolRadios = self.view.linear_tab.dir_rad
        dir_rad.bind_callback(callback=partial(self.radio_callback, motor="s2"))

        set_btn: SendButton = self.view.linear_tab.set_button
        set_btn.bind_callback(callback=self.model.s2.set_home)

        hom_btn: SendButton = self.view.linear_tab.hom_button
        hom_btn.bind_callback(callback=self.model.s2.go_home)

        is_on_btn: OnOffButton = self.view.linear_tab.toggle_button
        is_on_btn.bind_callback(callback=partial(self.on_off_callback, motor="s2"))

    def bind_rotation_tab(self) -> None:
        components: dict[str, dict[str, Widget]] = (
            self.view.rotation_tab.param_frame.components
        )
        self._bind_components(motor="s1", components=components)

        dir_rad: BoolRadios = self.view.rotation_tab.dir_rad
        dir_rad.bind_callback(callback=partial(self.radio_callback, motor="s1"))

        is_on_btn: OnOffButton = self.view.rotation_tab.toggle_button
        is_on_btn.bind_callback(callback=partial(self.on_off_callback, motor="s1"))

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

        if self.thread.connection and self.thread.connection.is_open:
            self.thread.connection.close()
            print("Disconnected from serial port.")
        self.thread.connection = None

        try:
            conn: serial.Serial = serial.Serial(
                port=selection, baudrate=115200, timeout=0.05
            )
            self.thread.connection = conn
            print(f"Connected to {selection}")
        except serial.SerialException as e:
            print(f"Failed to connect to {selection}: {e}")
