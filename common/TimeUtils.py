import time
from common.Logger import Logger
from datetime import datetime


def format_date_now(date_format="%Y-%m-%d") -> str:
    return time.strftime(date_format, time.localtime())


def validate_convert_date(date, date_format="%Y-%m-%d") -> datetime:
    """
    检查并检查 date 是否符合格式要求
    :param date_format: 日期格式, 默认为 "%Y-%m-%d" 即 YYYY-MM-DD
    :param date: 日期
    :return: datetime 对象 如果 date 符合格式要求, 否则抛出异常
    """
    try:
        # 尝试将 date 转换为 datetime 对象
        return datetime.strptime(date, date_format)
    except ValueError:
        raise ValueError(
            f"Invalid date format: {date}. Expected format: YYYY-MM-DD")


def validate_dates(start_date: str = None, end_date: str = None):
    """
    检查 start_date 和 end_date 是否符合格式要求，并且 start_date 早于或等于 end_date
    日期格式: YYYY-MM-DD
    :param start_date: 开始日期, 为None时不检查
    :param end_date: 结束日期, 为None时不检查
    :return: (True, None) 如果 start_date 和 end_date 符合格式要求, 否则 (False, 错误信息)
    """
    date_format = "%Y-%m-%d"

    try:
        if start_date:
            start_dt = validate_convert_date(start_date, date_format)
        else:
            start_dt = None

        if end_date:
            end_dt = validate_convert_date(end_date, date_format)
        else:
            end_dt = None

        if start_dt and end_dt:
            # 检查 start_date 是否早于或等于 end_date
            if start_dt > end_dt:
                raise ValueError(
                    "start_date should not be later than end_date.")
    except Exception as e:
        return False, e

    return True, None


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
