import time
from common.Logger import Logger
from common.TimeUtils import format_all_time


class Timer:
    def __init__(self, logger: Logger = None) -> None:
        self.time_start = time.time()
        self.time_cur = time.time()
        self.time_end = None
        self.logger = logger

    def lap(self):
        self.time_cur = time.time()

    def lap_and_show(self, message="Lap time"):
        time_now = time.time()
        time_cost = time_now - self.time_cur
        msg = f'{message}: {format_all_time(time_cost)}'
        if self.logger:
            self.logger.info_print(msg)
        else:
            print(msg)
        self.time_cur = time_now

    def end(self):
        self.time_end = time.time()

    def end_and_show(self):
        self.end()
        self.show_time_cost()

    def show_time_cost(self, message="Time cost"):
        time_cost_in_seconds = time.time() - self.time_start
        msg = f'{message}: {format_all_time(time_cost_in_seconds)}'
        if self.logger:
            self.logger.info_print(msg)
        else:
            print(msg)
