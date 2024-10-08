# Git Utils

# 完整依赖安装

```shell
pip install -r requirements.txt
```

# 使用方式

## 分割c/cpp的多个文件 `split-cpp-files.py`

在 [`split-cpp-files.py`](split-cpp-files.py) 文件中配置相关参数，然后直接运行脚本即可

```shell
python3 split-cpp-files.py
```

## 分割c/cpp的模块 `split-cpp-modules.py`

在 [`split-cpp-modules.py`](split-cpp-modules.py) 文件中配置相关参数，然后直接运行脚本即可

```shell
python3 split-cpp-modules.py
```

## 分割单个模块 `split-module.py`

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
```

## 分割多个文件或模块 `split-files.py`

安装依赖
- 相关链接：https://github.com/newren/git-filter-repo?tab=readme-ov-file
- git >= 2.22.0 at a minimum; 
- some features require git >= 2.24.0 or later
- python3 >= 3.5

```shell
pip install git-filter-repo
# or
pip3 install git-filter-repo
```

pip3安装

```shell
sudo apt update
sudo apt install python3-pip
pip3 --version
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

# 示例1 服务器96 多行命令 分割多个文件+模块
python3 split-files.py \
-o /home/fdse/fudan_kernel/repo/linux-stable \
-tps include/linux mm/ksm.c mm/memory.c \
-nn linux-stable-split-demo1 \
-nl /home/fdse/code-wisdom-installer/repository \
-nb demo1
# 示例2 windows 单行命令 分割多个文件+模块
python3 split-files.py -o D:/coding/zhurong-CodeWisdom/test_codes/linux-stable -tps include/linux mm/ksm.c mm/memory.c -nn linux-stable-demo1 -nl D:/coding/zhurong-CodeWisdom/test_codes -nb demo1
```