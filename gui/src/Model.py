from queue import Queue


class MotorControllerModel:
    def __init__(self, queue: Queue[str]) -> None:
        self.queue: Queue[str] = queue

        self._s1_max: float = 0.0
        self._s1_spd: float = 0.0

        self._s2_max: float = 0.0
        self._s2_acc: float = 0.0
        self._s2_end: int = 0
        self._s2_mov: int = 0
        self._s2_mtp: int = 0
        self._s2_mta: int = 0

        self.s1_is_on: bool = False
        self.s1_dir_multiplier: int = 1

        self.s2_is_on: bool = False
        self.s2_dir_multiplier: int = 1

    ################################################
    # Stepper 2 Properties
    ################################################
    def _send_to_queue(self, cmd_prefix: str, value: float | int) -> None:
        arduino_cmd: str = f"{cmd_prefix}={value}\n"
        self.queue.put(item=arduino_cmd)

    ################################################
    # Stepper 1 Properties
    ################################################
    @property
    def s1_max(self) -> float:
        return self._s1_max

    @s1_max.setter
    def s1_max(self, value: float) -> None:
        self._s1_max = value
        self._send_to_queue(cmd_prefix="S1_MAX", value=value)

    @property
    def s1_spd(self) -> float:
        return self._s1_spd

    @s1_spd.setter
    def s1_spd(self, value: float) -> None:
        self._s1_spd = value
        self._send_to_queue(cmd_prefix="S1_SPD", value=value)

    ################################################
    # Stepper 2 Properties
    ################################################
    @property
    def s2_max(self) -> float:
        return self._s2_max

    @s2_max.setter
    def s2_max(self, value: float) -> None:
        self._s2_max = value
        self._send_to_queue(cmd_prefix="S2_MAX", value=value)

    @property
    def s2_acc(self) -> float:
        return self._s2_acc

    @s2_acc.setter
    def s2_acc(self, value: float) -> None:
        self._s2_acc = value
        self._send_to_queue(cmd_prefix="S2_ACC", value=value)

    @property
    def s2_end(self) -> int:
        return self._s2_end

    @s2_end.setter
    def s2_end(self, value: int) -> None:
        self._s2_end = value
        self._send_to_queue(cmd_prefix="S2_END", value=value)

    @property
    def s2_mov(self) -> int:
        return self._s2_mov

    @s2_mov.setter
    def s2_mov(self, value: int) -> None:
        self._s2_mov = value
        self._send_to_queue(cmd_prefix="S2_MOV", value=value)

    @property
    def s2_mtp(self) -> int:
        return self._s2_mtp

    @s2_mtp.setter
    def s2_mtp(self, value: int) -> None:
        self._s2_mtp = value
        self._send_to_queue(cmd_prefix="S2_MTP", value=value)

    @property
    def s2_mta(self) -> int:
        return self._s2_mta

    @s2_mta.setter
    def s2_mta(self, value: int) -> None:
        self._s2_mta = value
        self._send_to_queue(cmd_prefix="S2_MTA", value=value)

    ################################################
    # Non-Value Functions
    ################################################
    def s2_set_home(self) -> None:
        self._send_to_queue(cmd_prefix="S2_SET", value=0)

    def s2_go_home(self) -> None:
        self._send_to_queue(cmd_prefix="S2_HOM", value=0)

    def s2_reset(self) -> None:
        self._send_to_queue(cmd_prefix="S2_RST", value=0)

    def reset_board(self) -> None:
        self._send_to_queue(cmd_prefix="RESET", value=0)
