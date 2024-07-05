# Git Utils

# 使用方式

## 分割模块 `split-module.py`

```shell
python3 split-module.py -o <path_to_original_repo> -m <module_path> -nn <new_repo_name> -nl <new_repo_location>

# 示例1：linux 多行命令
python3 split-module.py \
-o /home/fdse/code-wisdom-installer/repository/OS-23Fall-FDU \
-m src/fs \
-nn OS-23Fall-FDU-fs-only \
-nl /home/fdse/code-wisdom-installer/repository

# 示例2：windows 单行命令
python3 split-module.py -o D:/coding/zhurong-CodeWisdom/test_codes/OS-23Fall-FDU -m src/fs -nn fs-only-rejoin -nl D:/coding/zhurong-CodeWisdom/test_codes

python3 split-module.py \
-o /home/fdse/code-wisdom-installer/repository/OS-23Fall-FDU \
-m src/kernel \
-nn OS-23Fall-FDU-temp \
-nl /home/fdse/code-wisdom-installer/repository

python3 split-module.py -o D:/coding/zhurong-CodeWisdom/test_codes/OS-23Fall-FDU -m src/kernel -nn OS-23Fall-FDU-kernel-only -nl D:/coding/zhurong-CodeWisdom/test_codes

python3 split-module.py -o D:/coding/zhurong-CodeWisdom/test_codes/OS-23Fall-FDU -m src/kernel -nn OS-23Fall-FDU-temp -nl D:/coding/zhurong-CodeWisdom/test_codes
```

## 分割多个文件 `split-files.py`

安装依赖
- 相关链接：https://github.com/newren/git-filter-repo?tab=readme-ov-file
- git >= 2.22.0 at a minimum; 
- some features require git >= 2.24.0 or later
- python3 >= 3.5

```shell
pip install git-filter-repo
```

```shell
# 其中<target_paths>可以指定多个值，使用空格分割
python3 split-files.py \
-o <path_to_original_repo> \
-tps <target_paths> \
-nn <new_repo_name> \
-nl <new_repo_location> \
-nb <new_branch_name>

# 其中<target_paths>可以指定多个值，使用空格分割
python3 split-files.py -o <path_to_original_repo> -tps <target_paths> -nn <new_repo_name> -nl <new_repo_location> -nb <new_branch_name>

# 示例1 服务器96 多行命令
python3 split-files.py \
-o /home/fdse/fudan_kernel/repo/linux-stable \
-tps include/linux/ksm.h mm/ksm.c mm/memory.c \
-nn linux-stable-split-demo1 \
-nl /home/fdse/code-wisdom-installer/repository \
-nb demo1
python3 split-files.py \
-o /home/fdse/code-wisdom-installer/repository/OS-23Fall-FDU-temp \
-tps console.c \
-nn OS-23Fall-FDU-temp-split \
-nl /home/fdse/code-wisdom-installer/repository \
-nb split
# 示例2 windows 单行命令
python3 split-files.py -o D:/coding/zhurong-CodeWisdom/test_codes/linux-stable -tps include/linux/ksm.h mm/ksm.c mm/memory.c -nn linux-stable-demo1 -nl D:/coding/zhurong-CodeWisdom/test_codes -nb demo1
# 示例3 demo1
python3 split-files.py -o D:/coding/zhurong-CodeWisdom/test_codes/linux-stable-original -tps include/linux/ksm.h mm/ksm.c mm/memory.c -nn linux-stable-demo1-temp -nl D:/coding/zhurong-CodeWisdom/test_codes -nb temp
# 示例4 分割 sd.c 用于debug cpp-parser 
python3 split-files.py -o D:/coding/zhurong-CodeWisdom/test_codes/OS-23Fall-FDU -tps src/driver/sd.c -nn OS-23Fall-FDU-sd-only -nl D:/coding/zhurong-CodeWisdom/test_codes -nb sd
# 示例4 分割 sd.c 用于debug cpp-parser -tps 指定一个文件，一个目录
python3 split-files.py -o D:/coding/zhurong-CodeWisdom/test_codes/OS-23Fall-FDU -tps src/driver/sd.c src/fs -nn OS-23Fall-FDU-temp1 -nl D:/coding/zhurong-CodeWisdom/test_codes -nb temp1
```