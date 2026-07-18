import threading
import time
from queue import Empty, Full, Queue

import serial
import serial.tools.list_ports
from gui.src.model import Model
from serial.tools.list_ports_common import ListPortInfo
from typing_extensions import override  # pyright: ignore[reportMissingModuleSource]


class SerialWorker(threading.Thread):
    def __init__(self, model: Model, inbox: Queue[str], outbox: Queue[str]) -> None:
        super().__init__(name="serial_worker", daemon=True)

        self.model: Model = model
        self.inbox: Queue[str] = inbox
        self.outbox: Queue[str] = outbox

        self._stop_event: threading.Event = threading.Event()
        self.connection: serial.Serial | None = None

        self.write_delay: float = 0.05
        self.port_check_delay: float = 1.0

    @override
    def run(self) -> None:

        last_port_check: float = 0.0
        last_write_time: float = 0.0

        while not self._stop_event.is_set():
            now: float = time.monotonic()

            if now - last_port_check >= self.port_check_delay:
                self._update_ports()
                last_port_check = now

            if self.connection is not None and self.connection.is_open:
                try:
                    if self.connection.in_waiting > 0:
                        line_bytes: bytes = self.connection.readline()
                        line_str: str = line_bytes.decode(
                            encoding="ascii", errors="ignore"
                        ).strip()

                        if line_str:
                            try:
                                self.inbox.put_nowait(item=line_str)
                            except Full:
                                pass

                    if now - last_write_time >= self.write_delay:
                        try:
                            cmd: str = self.outbox.get_nowait()
                            _ = self.connection.write(cmd.encode(encoding="ascii"))
                            last_write_time = now
                        except Empty:
                            pass

                except serial.SerialException:
                    self.connection.close()
                    self.connection = None

            time.sleep(0.01)

    def _update_ports(self) -> None:
        current_ports: list[ListPortInfo] = serial.tools.list_ports.comports()
        device_list: list[str] = [port.device for port in current_ports]

        if device_list != self.model.available_ports:
            self.model.available_ports = device_list

    def stop(self) -> None:
        self._stop_event.set()
