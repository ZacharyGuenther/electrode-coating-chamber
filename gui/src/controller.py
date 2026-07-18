from gui.src.model import Model
from gui.src.serial_threads import SerialWorker
from gui.src.view import View


class Controller:
    def __init__(self, view: View, model: Model) -> None:
        self.thread: SerialWorker = SerialWorker()
