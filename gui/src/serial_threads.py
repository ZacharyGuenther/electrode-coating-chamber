import threading

import serial
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo


class SerialWorker(threading.Thread):
    def __init__(self) -> None:
        super().__init__(target=self._check_loop, daemon=True)

        self._lock: threading.Lock = threading.Lock()
        self._stop_event: threading.Event = threading.Event()

        self._cached_ports: list[ListPortInfo] = []
        self._new_ports: bool = False

    def _check_loop(self) -> None:
        while not self._stop_event.is_set():
            current_ports: list[ListPortInfo] = serial.tools.list_ports.comports()

            with self._lock:
                if [p.device for p in self._cached_ports] != [
                    p.device for p in current_ports
                ]:
                    self._cached_ports = current_ports
                    self._new_ports = True

            _ = self._stop_event.wait(timeout=0.2)

    def update_ports(self, current_ports: list[ListPortInfo]) -> list[ListPortInfo]:
        with self._lock:
            if self._new_ports:
                self._new_ports = False
                return self._cached_ports.copy()
            return current_ports

    def stop(self) -> None:
        self._stop_event.set()
        self.join()
