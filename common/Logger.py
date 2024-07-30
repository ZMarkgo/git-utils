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
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        info = f"[{time_str}] [{self.TAG}] {info}"
        self.log_buffer.append(info)
        if flush or len(self.log_buffer) >= self.MAX_LOG_BUFFER_SIZE or len(info) >= self.MAX_LOG_BUFFER_STR_LEN:
            with open(self.log_file_path, 'a') as f:
                for log in self.log_buffer:
                    f.write(log + '\n')
                f.write(info + '\n')
            self.log_buffer.clear()
