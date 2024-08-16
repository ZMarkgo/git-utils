import os
from datetime import datetime
from common.TimeUtils import format_date_now
import threading
import traceback


DEFAULT_LOG_FILE_PATH = './logs/log.log'
# 默认时间格式，用于日志记录，带有年月日时分秒毫秒
DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class LogBuffer:
    def __init__(self, max_log_buffer_size=100, max_log_buffer_str_len=1000):
        self.log_buffer = []
        self.log_buffer_str_len = 0
        self.MAX_LOG_BUFFER_SIZE = max_log_buffer_size
        self.MAX_LOG_BUFFER_STR_LEN = max_log_buffer_str_len

    def append(self, msg):
        self.log_buffer.append(msg)
        self.log_buffer_str_len += len(msg)

    def is_full(self):
        return len(self.log_buffer) >= self.MAX_LOG_BUFFER_SIZE or self.log_buffer_str_len >= self.MAX_LOG_BUFFER_STR_LEN

    def clear(self):
        self.log_buffer.clear()
        self.log_buffer_str_len = 0

    def __len__(self):
        return len(self.log_buffer)

    def __iter__(self):
        return iter(self.log_buffer)


class ThreadSafeLogBuffer(LogBuffer):
    def __init__(self, max_log_buffer_size=100, max_log_buffer_str_len=1000):
        super().__init__(max_log_buffer_size, max_log_buffer_str_len)
        self.lock = threading.Lock()  # 创建一个锁

    def append(self, msg):
        with self.lock:  # 在修改共享资源前加锁
            super().append(msg)

    def is_full(self):
        with self.lock:  # 访问共享资源时加锁
            return super().is_full()

    def clear(self):
        with self.lock:  # 在修改共享资源前加锁
            super().clear()

    def __len__(self):
        with self.lock:  # 访问共享资源时加锁
            return super().__len__()

    def __iter__(self):
        with self.lock:  # 迭代时加锁，确保一致性
            return super().__iter__()


class LogMetaInfo:
    def __init__(self, file) -> None:
        self.current_file_name = file.replace('\\', '/').split('/')[-1]
        self.file_tag = self.current_file_name
        self.date_now = format_date_now()
        self.log_file_path = os.path.abspath(
            f"./logs/{self.date_now}-{self.current_file_name}.log")

    def get_current_file_name(self):
        return self.current_file_name

    def get_file_tag(self):
        return self.file_tag

    def get_date_now(self):
        return self.date_now

    def get_log_file_path(self, file_prefix="", file_suffix="", file_extension=".log"):
        prefix = f"{file_prefix}-" if file_prefix else ""
        suffix = f"-{file_suffix}" if file_suffix else ""
        return os.path.abspath(f"./logs/{prefix}{self.date_now}-{self.current_file_name}{suffix}{file_extension}")


class Logger:
    def __init__(self, tag='', log_file_path=DEFAULT_LOG_FILE_PATH,
                 time_format=DEFAULT_TIME_FORMAT,
                 log_buffer: LogBuffer = None,
                 error_print_and_ignore: bool = False,
                 max_log_buffer_size: int = 100, max_log_buffer_str_len: int = 1000):
        """
        :param tag: 日志标签
        :param log_file_path: 日志文件路径
        :param time_format: 时间格式
        :param log_buffer: 日志缓存, 为None则使用LogBuffer
        :param error_print_and_ignore: 是否打印并忽略异常
        :param max_log_buffer_size: 日志缓存最大长度
        :param max_log_buffer_str_len: 日志缓存最大字符长度
        """
        self.tag = tag
        self.log_file_path = log_file_path
        self.time_format = time_format
        if log_buffer is None:
            self.log_buffer = LogBuffer(
                max_log_buffer_size, max_log_buffer_str_len)
        else:
            self.log_buffer = log_buffer

        self.error_print_and_ignore = error_print_and_ignore
        if not os.path.exists(os.path.dirname(self.log_file_path)):
            os.makedirs(os.path.dirname(self.log_file_path))

        with open(self.log_file_path, 'a') as f:
            f.write('')

        self.info_print(
            f"Logger created, log file path: {self.log_file_path}, \
            time format: {self.time_format}, \
            tag: {self.tag}, \
            error_print_and_ignore: {self.error_print_and_ignore}, \
            max_log_buffer_size: {max_log_buffer_size}, \
            max_log_buffer_str_len: {max_log_buffer_str_len}, \
            log_buffer: {type(self.log_buffer).__name__}")

    def format_info(self, info):
        current_time = datetime.now().strftime(self.time_format)
        return f"{current_time} [{self.tag}] INFO {info}"

    def format_warning(self, warning):
        current_time = datetime.now().strftime(self.time_format)
        return f"{current_time} [{self.tag}] WARNING {warning}"

    def format_error(self, error):
        current_time = datetime.now().strftime(self.time_format)
        return f"{current_time} [{self.tag}] ERROR {error}"

    def log_msg(self, msg, flush=True, stdout=False):
        """
        记录一条日志到日志文件
        :param msg: 日志信息
        :param flush: 是否立即写入文件
        :param stdout: 是否输出到标准输出
        """
        self.log_buffer.append(msg)
        if flush or self.log_buffer.is_full():
            self.flush()
        if stdout:
            print(msg, flush=True)

    def info(self, msg, flush=True, stdout=False):
        """
        记录info级别, 格式化的msg日志, 到日志文件
        :param info: 日志信息
        :param flush: 是否立即写入文件
        :param stdout: 是否输出到标准输出
        """
        self.log_msg(self.format_info(msg), flush, stdout)

    def warning(self, msg, flush=True, stdout=False):
        """
        记录warning级别, 格式化的msg日志, 到日志文件
        :param warning: 警告信息
        :param flush: 是否立即写入文件
        :param stdout: 是否输出到标准输出
        """
        self.log_msg(self.format_warning(msg), flush, stdout)

    def error(self, msg, flush=True, stdout=False):
        """
        记录error级别, 格式化的msg日志, 到日志文件
        :param error: 错误信息
        :param flush: 是否立即写入文件
        :param stdout: 是否输出到标准输出
        """
        self.log_msg(self.format_error(msg), flush, stdout)

    def info_print(self, msg, flush=True):
        """
        标准输出，并记录日志
        :param info: 日志信息
        :param flush: 是否立即输出
        """
        self.info(msg, flush, stdout=True)

    def warning_print(self, msg, flush=True):
        """
        标准输出警告，并记录日志
        :param warning: 警告信息
        :param flush: 是否立即输出
        """
        self.warning(msg, flush, stdout=True)

    def error_print(self, msg, flush=True):
        """
        标准输出错误，并记录日志
        :param error: 错误信息
        :param flush: 是否立即输出
        """
        self.error(msg, flush, stdout=True)

    def flush(self):
        """
        将所有缓存中的日志写入文件
        """
        with open(self.log_file_path, 'a') as f:
            for log in self.log_buffer:
                f.write(log + '\n')
        self.log_buffer.clear()

    def __enter__(self):
        """
        进入上下文管理器
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        退出上下文管理器
        """
        self.flush()

        # 打印异常的详细信息
        if exc_type is not None and self.error_print_and_ignore:
            self.error_print("Exception occurred:", flush=True)
            exception_info = traceback.format_exception(
                exc_type, exc_value, exc_traceback)
            for line in exception_info:
                self.log_msg(msg=line, flush=True, stdout=True)

        # 在__exit__中，如果要抑制异常，返回 True，否则返回 False
        return self.error_print_and_ignore


class LoggerFactory:

    log_file_path: str = DEFAULT_LOG_FILE_PATH
    thread_safe_log_buffer: ThreadSafeLogBuffer = ThreadSafeLogBuffer()

    @classmethod
    def main_set_log_file_path(cls, log_file_path):
        cls.log_file_path = log_file_path

    @classmethod
    def create_logger(cls, tag='', time_format=DEFAULT_TIME_FORMAT):
        return Logger(tag=tag, log_file_path=cls.log_file_path, time_format=time_format, log_buffer=cls.thread_safe_log_buffer)
