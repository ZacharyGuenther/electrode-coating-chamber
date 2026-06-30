import serial
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo


class serial_worker(serial.Serial):
    port_devices: list[str]

    def __init__(self, **kwargs) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        super().__init__(**kwargs)  # pyright: ignore[reportUnknownArgumentType]

        self.port_devices = [""]

    def get_port_devices(self) -> list[str]:
        raw_ports: list[ListPortInfo] = serial.tools.list_ports.comports()
        self.port_devices = [raw_port.device for raw_port in raw_ports]
        return self.port_devices

    def set_port(self, selected_port: str) -> None:
        self.close()
        self.port: str = selected_port
        self.open()
