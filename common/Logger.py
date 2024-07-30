import os
import time


class Logger:
    def __init__(self, tag='', log_file_path='./logs/log.log', max_log_buffer_size=100, max_log_buffer_str_len=1000):
        self.TAG = tag
        self.log_file_path = log_file_path
        self.log_buffer = []
        self.MAX_LOG_BUFFER_SIZE = max_log_buffer_size
        self.MAX_LOG_BUFFER_STR_LEN = max_log_buffer_str_len
        if not os.path.exists(os.path.dirname(self.log_file_path)):
            os.makedirs(os.path.dirname(self.log_file_path))
        with open(self.log_file_path, 'w') as f:
            f.write("")

    def info(self, info, flush=True):
        """
        记录日志，输出到文件中
        :param info: 日志信息
        :param flush: 是否立即写入文件
        """
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        info = f"[{time_str}] [{self.TAG}] {info}"
        self.log_buffer.append(info)
        if flush or len(self.log_buffer) >= self.MAX_LOG_BUFFER_SIZE or len(info) >= self.MAX_LOG_BUFFER_STR_LEN:
            self.flush()

    def info_print(self, info, flush=True):
        """
        标准输出，并记录日志
        :param info: 日志信息
        :param flush: 是否立即输出
        """
        print(info, flush=flush)
        self.info(info, flush)

    def flush(self):
        """
        强制写入文件
        """
        with open(self.log_file_path, 'a') as f:
            for log in self.log_buffer:
                f.write(log + '\n')
        self.log_buffer.clear()

    def close(self):
        """
        显式关闭日志
        """
        self.flush()
