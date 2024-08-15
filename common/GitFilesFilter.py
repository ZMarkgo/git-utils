import os
import sys
import subprocess
from common.GitUtils import copy_dir, remove_dir, list_gitignore_files, get_repo_size_info, get_repo_size_change_info, remove_all_git_remotes, add_virtual_remote, create_branch, format_get_commit_count_msg, format_get_earliest_commit_date_msg
from common.GitUtils import format_count_files_commits_msg
from common.PrintUtils import get_sep, print_sep
from common.FileUtils import remove_prefix_slash_and_dot, count_all_file_ext, format_file_ext_count_msg
from common.CppHeaderUtils import get_relative_headers_of_files, get_relative_headers_of_files_all_commits, get_relative_headers_of_modules
from common.Logger import Logger, LoggerFactory, LogMetaInfo
from common.TimeUtils import Timer
import traceback

# 日志配置信息
log_meta_info = LogMetaInfo(__file__)
CURRENT_FILE_NAME = log_meta_info.get_current_file_name()
TAG = log_meta_info.get_file_tag()
LOG_FILE_PATH = log_meta_info.get_log_file_path()


def split_files(original_repo_path="", target_paths: list = [],
                new_repo_name="", new_repo_location="", new_branch_name="",
                track_gitignore=False,
                timer: Timer = None,
                preserve_commit_hashes=True,
                regex_with_glob=False):
    """
    通用方法，用于提取指定文件及其历史记录到新的仓库
    """
    with LoggerFactory.create_logger(f"{TAG}#split_files") as logger:
        if timer is None:
            timer = Timer(logger=logger)

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
        timer.lap_and_show("Check parameters")

        logger.info_print(get_sep("复制仓库"))
        # 复制原始仓库到新的位置
        new_repo_path = os.path.join(new_repo_location, new_repo_name)
        logger.info_print(f"Original repo path: {original_repo_path}")
        logger.info_print(f"New repo location: {new_repo_path}")
        copy_dir(original_repo_path, new_repo_path)

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
            logger.info_print(
                f"Target .gitignore file num: {len(gitignore_files)}")
            logger.info(f"Target .gitignore files: {gitignore_files}")
        # 保留原始提交哈希，而不是生成新的提交哈希
        if preserve_commit_hashes:
            split_cmd.extend(['--preserve-commit-hashes'])
        split_cmd.extend(['--force'])
        logger.info_print(f"Target path and path-glob num: {target_num}")
        logger.info(f"Running command: {' '.join(split_cmd)}")
        subprocess.run(split_cmd, check=True)

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

        timer.lap_and_show("Slim repo")

        # 为新仓库添加虚拟远程仓库
        logger.info_print(get_sep("添加虚拟远程仓库"))
        remove_all_git_remotes()
        add_virtual_remote(new_repo_name)

        timer.lap_and_show("Add virtual remote")

        # 创建新分支
        logger.info_print(get_sep("创建新分支"))
        logger.info_print(f"New branch name: {new_branch_name}")
        create_branch(new_branch_name)

        timer.lap_and_show("Create new branch")

        logger.info_print(get_sep("处理完成"))


def statistics_split_info(repo_path, cpp_file_relative_paths, timer: Timer = None):
    with LoggerFactory.create_logger(f"{TAG}#statistics_split_info") as logger:
        if timer is None:
            timer = Timer(logger=logger)

        logger.info_print("Start statistics split info")

        logger.info_print(get_sep("Counting all files"))
        timer.lap()
        all_file_ext_counts = count_all_file_ext(repo_path)
        # 展示所有文件类型的文件数量
        for file_ext, count in all_file_ext_counts.items():
            logger.info_print(format_file_ext_count_msg(file_ext, count))
        timer.lap_and_show('Counting all files')

        logger.info_print(get_sep("Counting all commits"))
        timer.lap()
        logger.info_print(format_get_commit_count_msg(repo_path))
        timer.lap_and_show('Counting all commits')

        logger.info_print(get_sep("Counting commits of target files"))
        timer.lap()
        logger.info_print(format_count_files_commits_msg(
            repo_path, cpp_file_relative_paths))
        timer.lap_and_show('Counting commits of target files')

        logger.info_print(get_sep("Showing earliest commit time"))
        timer.lap()
        logger.info_print(format_get_earliest_commit_date_msg(repo_path))
        timer.lap_and_show('Showing earliest commit time')

        timer.end()
        timer.show_time_cost()


def split_cpp_files(repo_path, include_dirs_relative_pahts, target_c_files,
                    new_repo_name, new_repo_location, new_branch_name,
                    track_gitignore, regex_with_glob, timer: Timer):
    with LoggerFactory.create_logger(f"{TAG}#split_cpp_files") as logger:
        if timer is None:
            timer = Timer(logger=logger)
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
            logger.info_print(f"target file or dir num: {len(target_paths)}")
            timer.lap_and_show("Get headers")

            split_files(original_repo_path=repo_path,
                        target_paths=target_paths,
                        new_repo_name=new_repo_name,
                        new_repo_location=new_repo_location,
                        new_branch_name=new_branch_name,
                        track_gitignore=track_gitignore,
                        timer=timer,
                        regex_with_glob=regex_with_glob)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())
        finally:
            timer.end()
            timer.show_time_cost()

        try:
            new_repo_path = f"{new_repo_location}/{new_repo_name}"
            statistics_split_info(new_repo_path, target_c_files, timer=timer)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())


# TODO 时间
def split_cpp_modules(repo_path, include_dirs_relative_pahts, modules: list,
                      new_repo_name, new_repo_location, new_branch_name,
                      track_gitignore, regex_with_glob, timer: Timer):
    with LoggerFactory.create_logger(f"{TAG}#split_cpp_modules") as logger:
        if timer is None:
            timer = Timer(logger=logger)

        try:
            timer.lap()
            target_paths = []
            # 基于当前版本分析得到目标模块下所有C/CPP文件需要的头文件（包括头文件嵌套的头文件）
            headers, unexist_headers, target_cpp_files = get_relative_headers_of_modules(
                repo_path, modules, include_dirs_relative_pahts,
                shouldRecursion=True)
            target_paths.extend(headers)
            target_paths.extend(modules)
            logger.info_print(f"target file or dir num: {len(target_paths)}")
            timer.lap_and_show("Get headers")

            timer.lap()
            logger.info(f"{len(headers)}, {headers}")
            logger.info(f"{len(unexist_headers)}, {unexist_headers}")
            logger.info(f"{len(target_cpp_files)}, {target_cpp_files}")
            timer.lap_and_show("Show headers and target files")

            split_files(original_repo_path=repo_path,
                        target_paths=target_paths,
                        new_repo_name=new_repo_name,
                        new_repo_location=new_repo_location,
                        new_branch_name=new_branch_name,
                        track_gitignore=track_gitignore,
                        timer=timer,
                        regex_with_glob=regex_with_glob)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())
        finally:
            timer.end()
            timer.show_time_cost()

        try:
            new_repo_path = f"{new_repo_location}/{new_repo_name}"
            statistics_split_info(new_repo_path, target_cpp_files, timer=timer)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())
