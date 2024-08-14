import os
import time

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


class Logger:
    def __init__(self, tag='', log_file_path='./logs/log.log',
                 time_format=DEFAULT_TIME_FORMAT,
                 max_log_buffer_size=100, max_log_buffer_str_len=1000):
        self.TAG = tag
        self.log_file_path = log_file_path
        self.time_format = time_format
        self.log_buffer = LogBuffer(
            max_log_buffer_size, max_log_buffer_str_len)

        if not os.path.exists(os.path.dirname(self.log_file_path)):
            os.makedirs(os.path.dirname(self.log_file_path))
        if not os.path.exists(self.log_file_path):
            os.mknod(self.log_file_path)

    def format_info(self, info):
        return f"{time.strftime(self.time_format, time.localtime())} [{self.TAG}] INFO {info}"

    def format_warning(self, warning):
        return f"{time.strftime(self.time_format, time.localtime())} [{self.TAG}] WARNING {warning}"

    def format_error(self, error):
        return f"{time.strftime(self.time_format, time.localtime())} [{self.TAG}] ERROR {error}"

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

    def __exit__(self, exc_type, exc_value, traceback):
        """
        退出上下文管理器
        """
        self.flush()
        # 可以处理异常
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")
        return True  # 如果要抑制异常，返回 True，否则返回 False
