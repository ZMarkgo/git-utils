#!/bin/bash

# 检查是否提供了命令行参数
if [ $# -eq 0 ]; then
    echo "Usage: $0 <command>"
    exit 1
fi

# 将所有命令行参数作为要执行的命令
command_to_run="$@"

echo "Command to run: '$command_to_run'"

# 获取当前时间戳（秒级）
start_time=$(date +%s)

# 执行命令
$command_to_run

# 获取当前时间戳（秒级）
end_time=$(date +%s)

# 计算执行时间
runtime=$((end_time - start_time))

echo "Command '$command_to_run' executed in $runtime seconds."

