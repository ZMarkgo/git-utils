import os
import sys
from common.GitUtils import copy_dir, remove_dir, list_gitignore_files, get_repo_size_info, get_repo_size_change_info, remove_all_git_remotes, add_virtual_remote, create_branch, format_get_commit_count_msg, format_get_earliest_commit_date_msg
from common.GitUtils import format_count_files_commits_msg
from common.PrintUtils import get_sep
from common.FileUtils import remove_prefix_slash_and_dot, count_all_file_ext, format_file_ext_count_msg
from common.CppHeaderUtils import get_relative_headers_of_files, get_relative_headers_of_files_all_commits, get_relative_headers_of_modules
from common.Logger import LoggerFactory, LogMetaInfo
from common.CmdUtils import run_cmd
from common.Timer import Timer
from common.TimeUtils import validate_dates
import traceback

# 日志配置信息
log_meta_info = LogMetaInfo(__file__)
CURRENT_FILE_NAME = log_meta_info.get_current_file_name()
TAG = log_meta_info.get_file_tag()
LOG_FILE_PATH = log_meta_info.get_log_file_path()


def split_files(original_repo_path="", target_paths: list = [],
                new_repo_name="", new_repo_location="", new_branch_name="",
                track_gitignore=False,
                preserve_commit_hashes=True,
                regex_with_glob=False,
                start_date=None, end_date=None):
    """
    通用方法，用于提取指定文件及其历史记录到新的仓库
    :param original_repo_path: 原始仓库绝对路径
    :param target_paths: 目标文件路径列表
    :param new_repo_name: 新仓库名称
    :param new_repo_location: 新仓库位置（所在文件夹的绝对路径）
    :param new_branch_name: 新分支名称
    :param track_gitignore: 是否跟踪 .gitignore 文件
    :param timer: 计时器
    :param preserve_commit_hashes: 是否保留原始提交哈希，而不是生成新的提交哈希
    :param regex_with_glob: 是否使用正则表达式匹配路径
    :param start_date: 起始日期, 格式为 'YYYY-MM-DD'
    :param end_date: 结束日期, 格式为 'YYYY-MM-DD'
    """
    with LoggerFactory.create_logger(f"{TAG}#split_files") as logger:
        def subprocess_stdout_handler(line):
            if '\r' in line:
                # 如果line中有\r，说明是进度信息，不换行
                print(line, end='')
            else:
                print(line)

        def subprocess_stderr_handler(line):
            logger.log_msg(line.strip(), stdout=True)

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
        # 检查 start_date 和 end_date 是否符合格式
        dates_valid, dates_error = validate_dates(start_date, end_date)
        if not dates_valid:
            logger.error_print(f"Invalid dates: {dates_error}")
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
        # 添加日期过滤
        # 实现上使用自定义回调函数
        # 参阅https://htmlpreview.github.io/?https://github.com/newren/git-filter-repo/blob/docs/html/git-filter-repo.html#CALLBACKS
        # 在 git-filter-repo 中使用 --commit-callback 参数，传入一个自定义的回调函数（字符串形式的python代码）
        # 提供了start_date或者end_date
        should_skip_condition = ""
        if start_date:
            should_skip_condition += f' commit_date < "{start_date}T00:00:00" or'
        if end_date:
            should_skip_condition += f' commit_date > "{end_date}T00:00:00" or'
        if should_skip_condition:
            # 去掉前置空格
            should_skip_condition = should_skip_condition[1:]
            # 去掉最后一个 or
            should_skip_condition = should_skip_condition[:-2]
            commit_callback = f"\
            import datetime\n\
            timestamp = int(commit.committer_date.split()[0])\n\
            commit_date = datetime.datetime.utcfromtimestamp(timestamp).strftime(\"%Y-%m-%dT%H:%M:%S\")\n\
            if {should_skip_condition}:\n\
            \tcommit.skip()"
            logger.info_print(f"commit_callback: \n{commit_callback}")
            split_cmd.extend(['--commit-callback', commit_callback])
        # 保留原始提交哈希，而不是生成新的提交哈希
        if preserve_commit_hashes:
            split_cmd.extend(['--preserve-commit-hashes'])
        split_cmd.extend(['--force'])
        logger.info_print(f"Target path and path-glob num: {target_num}")
        logger.info(f"Running command: {' '.join(split_cmd)}")
        run_cmd(cmd=split_cmd,
                stdout_handler=subprocess_stdout_handler,
                stderr_handler=subprocess_stderr_handler,
                check=True)

        timer.lap_and_show("Extract files and history")

        # 仓库瘦身
        logger.info_print(get_sep("仓库瘦身"))
        repo_size_before = get_repo_size_info()
        # 移除 filter-repo 残留数据
        remove_dir('.git/filter-repo')
        # 清理未使用的对象
        # git reflog expire --expire=now --all && git gc --prune=now --aggressive
        reflog_cmd = ['git', 'reflog', 'expire', '--expire=now', '--all']
        run_cmd(
            cmd=reflog_cmd,
            stdout_handler=subprocess_stdout_handler,
            stderr_handler=subprocess_stderr_handler,
            check=True
        )
        gc_cmd = ['git', 'gc', '--prune=now', '--aggressive']
        run_cmd(
            cmd=gc_cmd,
            stdout_handler=subprocess_stdout_handler,
            stderr_handler=subprocess_stderr_handler,
            check=True
        )
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


def statistics_split_info(repo_path, cpp_file_relative_paths):
    with LoggerFactory.create_logger(f"{TAG}#statistics_split_info") as logger:
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
                    track_gitignore, regex_with_glob):
    with LoggerFactory.create_logger(f"{TAG}#split_cpp_files") as logger:
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
                        regex_with_glob=regex_with_glob)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())
        finally:
            timer.end()
            timer.show_time_cost()

        try:
            new_repo_path = f"{new_repo_location}/{new_repo_name}"
            statistics_split_info(new_repo_path, target_c_files)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())


def split_cpp_modules(repo_path, include_dirs_relative_pahts, modules: list,
                      new_repo_name, new_repo_location, new_branch_name,
                      track_gitignore, regex_with_glob,
                      start_date=None, end_date=None):
    with LoggerFactory.create_logger(f"{TAG}#split_cpp_modules") as logger:
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
            logger.info(f"exist_headers: {len(headers)}, {headers}")
            logger.info(
                f"unexist_headers: {len(unexist_headers)}, {unexist_headers}")
            logger.info(
                f"target_cpp_files: {len(target_cpp_files)}, {target_cpp_files}")
            timer.lap_and_show("Show headers and target files")

            split_files(original_repo_path=repo_path,
                        target_paths=target_paths,
                        new_repo_name=new_repo_name,
                        new_repo_location=new_repo_location,
                        new_branch_name=new_branch_name,
                        track_gitignore=track_gitignore,
                        regex_with_glob=regex_with_glob,
                        start_date=start_date, end_date=end_date)
            # 统计新仓库信息
            new_repo_path = f"{new_repo_location}/{new_repo_name}"
            statistics_split_info(new_repo_path, target_cpp_files)
        except Exception as e:
            logger.error_print(f"Error: {e}")
            logger.error_print(traceback.format_exc())
        finally:
            timer.end()
            timer.show_time_cost()
