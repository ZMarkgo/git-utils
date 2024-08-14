#!/bin/bash

# 配置
logFilePath=/home/app/repository/git-utils/logs

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "Usage: back_run_cmd.sh <command>"
    return 1
fi

# 获取当前脚本的目录
script_dir=$(dirname "${BASH_SOURCE[0]}")
# run_cmd.sh 路径
RUN_CMD_SCRPIT="$script_dir/run_cmd.sh"
# 获取当前日期
currentDate=$(date +"%Y-%m-%d")
logFile=${logFilePath}/back_run_cmd.sh-${currentDate}.log
# 后台运行命令
echo "==================================================================================" >> $logFile
nohup $RUN_CMD_SCRPIT $@ >> $logFile 2>&1 &

# 输出后台运行的进程ID (PID)
pid=$!
echo "Command is running in the background with PID: $pid"