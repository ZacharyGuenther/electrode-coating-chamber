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
        self._connection_lock: threading.Lock = threading.Lock()
        self.connection: serial.Serial | None = None

        self.write_delay: float = 0.05
        self.port_check_delay: float = 1.0

    def connect(
        self, port: str, baudrate: int = 115200, timeout: float = 0.05
    ) -> str | None:
        with self._connection_lock:
            if self.connection is not None and self.connection.is_open:
                self.connection.close()
            try:
                self.connection = serial.Serial(
                    port=port, baudrate=baudrate, timeout=timeout
                )
                return None
            except serial.SerialException as e:
                self.connection = None
                return str(e)

    def disconnect(self) -> None:
        with self._connection_lock:
            if self.connection is not None and self.connection.is_open:
                self.connection.close()
            self.connection = None

    def is_connected(self) -> bool:
        with self._connection_lock:
            return self.connection is not None and self.connection.is_open

    @override
    def run(self) -> None:
        last_port_check: float = 0.0
        last_write_time: float = 0.0

        while not self._stop_event.is_set():
            now: float = time.monotonic()

            if now - last_port_check >= self.port_check_delay:
                self._update_ports()
                last_port_check = now

            with self._connection_lock:
                connection: serial.Serial | None = self.connection

            if connection is not None and connection.is_open:
                try:
                    if connection.in_waiting > 0:
                        incoming_bytes: bytes = connection.readline()
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
                            _ = connection.write(cmd.encode(encoding="ascii"))
                            last_write_time = now
                        except Empty:
                            pass

                except serial.SerialException:
                    with self._connection_lock:
                        if self.connection is connection:
                            connection.close()
                            self.connection = None

            time.sleep(0.01)

    def _update_ports(self) -> None:
        all_ports: list[ListPortInfo] = serial.tools.list_ports.comports()
        usb_ports: list[str] = []
        for port in all_ports:
            if port.vid is not None:
                usb_ports.append(port.device)

        if usb_ports != self.model.ports:
            self.model.ports = usb_ports

    def stop(self) -> None:
        self._stop_event.set()
