#!/bin/bash

# 检查是否提供了PID参数
if [ -z "$1" ]; then
  echo "Usage: $0 <PID>"
  exit 1
fi

PID=$1

# 检查PID是否有效
if ! ps -p $PID > /dev/null 2>&1; then
  echo "Process with PID $PID does not exist."
  exit 1
fi

echo "Waiting for process with PID: $PID to complete..."

# 使用 wait 命令等待指定的PID完成
while kill -0 $PID 2> /dev/null; do
  sleep 1
done

echo "Process with PID $PID has completed."
