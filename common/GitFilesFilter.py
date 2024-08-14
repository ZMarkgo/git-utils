import os
import sys
import subprocess
from common.GitUtils import copy_dir, remove_dir, list_gitignore_files, get_repo_size_info, get_repo_size_change_info, remove_all_git_remotes, add_virtual_remote, create_branch, show_commit_count, show_earliest_commit_time
from common.GitUtils import show_commit_count, show_count_files_commits, show_earliest_commit_time
from common.PrintUtils import get_sep, print_sep
from common.FileUtils import remove_prefix_slash_and_dot, show_count_file_ext
from common.GitFilesFilter import split_files, statistics_split_info
from common.CppHeaderUtils import get_relative_headers_of_files, get_relative_headers_of_files_all_commits
from common.Logger import Logger
from common.TimeUtils import Timer
import traceback
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
    """
    通用方法，用于提取指定文件及其历史记录到新的仓库
    """
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
            # 如果 target_file 路径中包含 .. 则使用文件名，否则使用文件路径
            if '..' in target_file:
                target = target_file_name
            else:
                target = target_file
            if target in added_targets_set:
                continue
            if not regex_with_glob:
                split_cmd.extend(['--path', target])
                target_num += 1
            else:
                split_cmd.extend(['--path', target])
                split_cmd.extend(['--path-glob', f'*/{target}'])
                target_num += 2
            added_targets_set.add(target)
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


def statistics_split_info(repo_path, cpp_file_relative_paths, timer: Timer = None):
    if not timer:
        timer = Timer()

    print_sep('count files')
    timer.lap()
    show_count_file_ext(repo_path, '.c')
    show_count_file_ext(repo_path, '.h')
    timer.lap_and_show('Counting .c and .h files')

    print_sep('count all commits')
    timer.lap()
    show_commit_count(repo_path)
    timer.lap_and_show('Counting all commits')

    print_sep('count commits of target files')
    timer.lap()
    show_count_files_commits(repo_path, cpp_file_relative_paths)
    timer.lap_and_show('Counting commits of target files')

    print_sep('show earliest commit time')
    timer.lap()
    show_earliest_commit_time(repo_path)
    timer.lap_and_show('Showing earliest commit time')

    timer.end()
    timer.show_time_cost()


def split_cpp_files(repo_path, include_dirs_relative_pahts, target_c_files,
                    new_repo_name, new_repo_location, new_branch_name,
                    track_gitignore, regex_with_glob, timer: Timer):
    if timer is None:
        timer = Timer()
    try:
        target_paths = target_c_files.copy()
        timer.lap()
        # 基于当前版本分析得到目标c文件所有的头文件（包括头文件嵌套的头文件），
        # 以及c文件提交历史中的头文件
        # headers = get_relative_headers_of_files_all_commits(
        #     repo_path, target_paths, include_dirs_relative_pahts,
        #     shouldRecursion=True, timer=timer)
        # 基于当前版本分析得到目标c文件所有的头文件（包括头文件嵌套的头文件）
        headers, _ = get_relative_headers_of_files(
            repo_path, target_paths, include_dirs_relative_pahts,
            shouldRecursion=True)
        target_paths.extend(headers)
        print(f"target file or dir num: {len(target_paths)}")
        timer.show_time_cost("Get headers")

        split_files(original_repo_path=repo_path,
                    target_paths=target_paths,
                    new_repo_name=new_repo_name,
                    new_repo_location=new_repo_location,
                    new_branch_name=new_branch_name,
                    track_gitignore=track_gitignore,
                    timer=timer,
                    regex_with_glob=regex_with_glob)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        timer.end()
        timer.show_time_cost()

    try:
        new_repo_path = f"{new_repo_location}/{new_repo_name}"
        statistics_split_info(new_repo_path, target_c_files, timer=timer)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
