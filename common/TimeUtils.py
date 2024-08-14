import time
from common.Logger import Logger


def format_time_in_seconds(seconds):
    return f'{seconds:.2f}s'


def format_time_in_minutes(seconds):
    return f'{seconds / 60:.2f}m'


def format_time_in_hours(seconds):
    return f'{seconds / 3600:.2f}h'


def format_time(seconds):
    if seconds < 60:
        return format_time_in_seconds(seconds)
    elif seconds < 3600:
        return format_time_in_minutes(seconds)
    else:
        return format_time_in_hours(seconds)


def format_all_time(seconds):
    return f'{format_time_in_seconds(seconds)} or {format_time_in_minutes(seconds)} or {format_time_in_hours(seconds)}'


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
