import os
import sys
import subprocess
from common.GitUtils import copy_dir, remove_dir, list_gitignore_files, get_repo_size_info, get_repo_size_change_info, remove_all_git_remotes, add_virtual_remote, create_branch, show_commit_count, show_earliest_commit_time
from common.TimeUtils import Timer
from common.PrintUtils import get_sep
from common.Logger import Logger
from common.FileUtils import remove_prefix_slash_and_dot
import time

CURRENT_FILE_NAME = __file__.split('/')[-1]
TAG = CURRENT_FILE_NAME
# 当前日期
DATE_NOW = time.strftime("%Y-%m-%d", time.localtime())
LOG_FILE_PATH = os.path.abspath(f"./logs/{CURRENT_FILE_NAME}-{DATE_NOW}.log")


def split_files(original_repo_path="", target_paths: list = [],
                new_repo_name="", new_repo_location="", new_branch_name="",
                track_gitignore=False,
                timer: Timer = None,
                preserve_commit_hashes=True,
                regex_with_glob=False):

    with Logger(tag=TAG, log_file_path=LOG_FILE_PATH) as logger:
        if timer:
            timer.lap()
        logger.info_print(get_sep("参数检查"))
        # 检查原始仓库是否存在
        if not os.path.isdir(os.path.join(original_repo_path, ".git")):
            logger.error_print(
                f"The path {original_repo_path} does not appear to be a Git repository.")
            sys.exit(1)
        # 检查list是否为空
        if not target_paths:
            logger.error_print("The target_paths list is empty.")
            sys.exit(1)
        # 检查新仓库名称是否为空
        if not new_repo_name:
            logger.error_print("The new_repo_name is empty.")
            sys.exit(1)
        # 检查新仓库位置是否存在
        if not os.path.isdir(new_repo_location):
            logger.error_print(f"The path {new_repo_location} does not exist.")
            sys.exit(1)
        # 检查新分支名称是否为空字符串
        if not new_branch_name:
            logger.error_print("The new_branch_name is empty.")
            sys.exit(1)
        if timer:
            timer.lap_and_show("Check parameters")

        logger.info_print(get_sep("复制仓库"))
        # 复制原始仓库到新的位置
        new_repo_path = os.path.join(new_repo_location, new_repo_name)
        logger.info_print(f"Original repo path: {original_repo_path}")
        logger.info_print(f"New repo location: {new_repo_path}")
        copy_dir(original_repo_path, new_repo_path)

        if timer:
            timer.lap_and_show("Copy repo")

        logger.info_print(get_sep("提取文件及其历史"))
        # 切换到仓库
        os.chdir(new_repo_path)
        # 使用 git filter-repo 提取指定文件的历史记录
        split_cmd = ['git', 'filter-repo']
        target_num = 0
        added_targets_set = set()
        for target_file in target_paths:
            # 处理路径分隔符
            target_file = target_file.replace('\\', '/')
            # 递归删除前置 '/' 和 './'
            target_file = remove_prefix_slash_and_dot(target_file)
            # 提取文件名
            target_file_name = target_file.split('/')[-1]
            # 已经添加过，跳过
            if target_file_name in added_targets_set:
                continue
            # 如果 target_file 路径中包含 .. 使用文件名，否则使用文件路径
            if '..' in target_file:
                target = target_file_name
            else:
                target = target_file
            split_cmd.extend(['--path', target])
            target_num += 1
            if regex_with_glob:
                split_cmd.extend(['--path-glob', f'*/{target}'])
                target_num += 1
            added_targets_set.add(target_file_name)
        if track_gitignore:
            # 保留所有 gitignore 文件
            gitignore_files = list_gitignore_files(new_repo_path)
            for gitignore_file in gitignore_files:
                split_cmd.extend(['--path', gitignore_file])
                target_num += 1
        # 保留原始提交哈希，而不是生成新的提交哈希
        if preserve_commit_hashes:
            split_cmd.extend(['--preserve-commit-hashes'])
        split_cmd.extend(['--force'])
        logger.info_print(f"Target path and path-glob num: {target_num}")
        logger.info(f"Running command: {' '.join(split_cmd)}")
        subprocess.run(split_cmd, check=True)

        if timer:
            timer.lap_and_show("Extract files and history")

        # 仓库瘦身
        logger.info_print(get_sep("仓库瘦身"))
        repo_size_before = get_repo_size_info()
        # 移除 filter-repo 残留数据
        remove_dir('.git/filter-repo')
        # 清理未使用的对象
        # git reflog expire --expire=now --all && git gc --prune=now --aggressive
        subprocess.run(['git', 'reflog', 'expire',
                        '--expire=now', '--all'], check=True)
        subprocess.run(['git', 'gc', '--prune=now',
                       '--aggressive'], check=True)
        repo_size_after = get_repo_size_info()
        change_info = get_repo_size_change_info(
            repo_size_before, repo_size_after)
        logger.info_print(change_info)

        if timer:
            timer.lap_and_show("Slim repo")

        # 为新仓库添加虚拟远程仓库
        logger.info_print(get_sep("添加虚拟远程仓库"))
        remove_all_git_remotes()
        add_virtual_remote(new_repo_name)

        if timer:
            timer.lap_and_show("Add virtual remote")

        # 创建新分支
        logger.info_print(get_sep("创建新分支"))
        logger.info_print(f"New branch name: {new_branch_name}")
        create_branch(new_branch_name)

        if timer:
            timer.lap_and_show("Create new branch")

        logger.info_print(get_sep("处理完成"))
        # 展示提交数
        show_commit_count()
        # 展示最早的提交时间
        show_earliest_commit_time()
