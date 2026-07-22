import threading
import time
from queue import Empty, Full, Queue

import serial
import serial.tools.list_ports
from gui.src.model import Model
from serial.tools.list_ports_common import ListPortInfo
from typing_extensions import override


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
                        incoming_bytes: bytes = self.connection.readline()
                        incoming_str: str = incoming_bytes.decode(
                            encoding="ascii", errors="ignore"
                        ).strip()

                        if incoming_str:
                            try:
                                self.inbox.put_nowait(item=incoming_str)
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
        all_ports: list[ListPortInfo] = serial.tools.list_ports.comports()
        usb_ports: list[str] = []
        for port in all_ports:
            if port.vid is not None:
                usb_ports = [port.device]
        # Consider having this go to the inbox and having the controller set the values
        # in Model. Shouldn't cause a race condition for now because the GUI is updated
        # via a setter method of this variable.
        if usb_ports != self.model.ports:
            self.model.ports = usb_ports

    def stop(self) -> None:
        self._stop_event.set()
