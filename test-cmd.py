import os
from common.Logger import Logger
from common.CmdUtils import run_cmd

CURRENT_FILE_NAME = __file__.split('/')[-1]
TAG = CURRENT_FILE_NAME
LOG_FILE_PATH = os.path.abspath(f"./logs/{CURRENT_FILE_NAME}.log")

if __name__ == "__main__":
    with Logger(tag=TAG, log_file_path=LOG_FILE_PATH) as logger:
        def stdout_handler(line):
            logger.info_print(line.strip())

        def stderr_handler(line):
            logger.error_print(line.strip())

        cmd = ["ls", "-l"]
        run_cmd(cmd, stdout_handler, stderr_handler)
        logger.info_print("Done.")