from queue import Full, Queue
from typing import Any, Callable

from typing_extensions import Self


class QueueProperty:
    def __init__(self, private_name: str) -> None:
        self.private_name: str = private_name
        self.public_name: str = ""

    def __set_name__(self, owner: Any, name: str) -> None:  # pyright: ignore[reportAny, reportExplicitAny]
        self.public_name = name.upper()

    def __get__(self, instance: Any, owner: Any) -> Self | Any:  # pyright: ignore[reportAny, reportExplicitAny]
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)  # pyright: ignore[reportAny]

    def __set__(self, instance: Any, value: int | float) -> None:  # pyright: ignore[reportAny, reportExplicitAny]
        setattr(instance, self.private_name, value)  # pyright: ignore[reportAny]
        full_prefix: str = f"{instance.prefix}_{self.public_name}"  # pyright: ignore[reportAny]
        instance._send_to_queue(cmd_prefix=full_prefix, value=value)  # pyright: ignore[reportAny]


class StepperMotor:
    max: QueueProperty = QueueProperty(private_name="_max")
    spd: QueueProperty = QueueProperty(private_name="_spd")
    acc: QueueProperty = QueueProperty(private_name="_acc")
    end: QueueProperty = QueueProperty(private_name="_end")
    mov: QueueProperty = QueueProperty(private_name="_mov")
    mtp: QueueProperty = QueueProperty(private_name="_mtp")
    mta: QueueProperty = QueueProperty(private_name="_mta")

    def __init__(
        self, queue: Queue[str], prefix: str, spr: float = 0.0, mmpr: float = 10000.0
    ) -> None:
        self.outbox: Queue[str] = queue
        self.prefix: str = prefix.upper()

        self._max: float = 0.0
        self._spd: float = 0.0
        self._acc: float = 0.0
        self._end: int = 0
        self._mov: int = 0
        self._mtp: int = 0
        self._mta: int = 0

        self.dir: int = 1
        self.is_on: bool = False

        self.stgd_max: float = 0.0
        self.stgd_spd: float = 0.0
        self.stgd_acc: float = 0.0
        self.stgd_end: int = 0
        self.stgd_mov: int = 0
        self.stgd_mtp: int = 0
        self.stgd_mta: int = 0

        # SPR = steps per revolution
        # SPMM = steps per millimeter
        # MMPR = millimeter per revolution
        self.SPR: float = spr
        self.MMPR: float = mmpr
        self.SPMM: float = self.SPR / self.MMPR

        self.conv_factors: dict[str, float] = {
            "mm": self.SPMM,
            "cm": (self.SPMM * 10.0),  # 10 mm/cm
            "step": 1.0,
            "RPM": (self.SPR / 60),
            "step/s": 1.0,
            "RPM/s": (self.SPR / 60),
            "step/s\u00b2": 1.0,
        }

    def _send_to_queue(self, cmd_prefix: str, value: float | int) -> None:
        try:
            arduino_cmd: str = f"{cmd_prefix}={value}\n"
            self.outbox.put_nowait(item=arduino_cmd)
        except Full:
            print("Queue is full!")

    def set_home(self, value: int | float = 0) -> None:
        full_prefix: str = f"{self.prefix}_SET"
        self._send_to_queue(cmd_prefix=full_prefix, value=value)

    def go_home(self, value: int | float = 0) -> None:
        full_prefix: str = f"{self.prefix}_HOM"
        self._send_to_queue(cmd_prefix=full_prefix, value=value)

    def reset(self, value: int | float = 0) -> None:
        full_prefix: str = f"{self.prefix}_RST"
        self._send_to_queue(cmd_prefix=full_prefix, value=value)

    def reset_board(self, value: int | float = 0) -> None:
        self._send_to_queue(cmd_prefix="RESET", value=value)


class Model:
    def __init__(self, queue: Queue[str]) -> None:
        self._ports: list[str] = []
        self._port_callback: Callable[[list[str]], None] | None = None

        self.s1: StepperMotor = StepperMotor(queue=queue, spr=200, prefix="S1")
        self.s2: StepperMotor = StepperMotor(queue=queue, spr=400, mmpr=60, prefix="S2")

    def bind_port_update(self, callback: Callable[[list[str]], None]) -> None:
        self._port_callback = callback

    @property
    def ports(self) -> list[str]:
        return self._ports

    @ports.setter
    def ports(self, new_ports: list[str]) -> None:
        self._ports = new_ports
        if self._port_callback is not None:
            self._port_callback(self._ports)
