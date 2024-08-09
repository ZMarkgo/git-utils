#!/bin/bash

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "Usage: run_cmd.sh <command>"
    return 1
fi

# 获取当前脚本的目录
script_dir=$(dirname "${BASH_SOURCE[0]}")

# 引入 measure_time.sh
source "$script_dir/measure_time.sh"

measure_time $@