import os
import re
from typing import Set, Tuple
from tqdm import tqdm
from common.GitUtils import get_file_commits, get_commit_diff
from common.TimeUtils import Timer


def normalize_path(path):
    """
    归一化路径分隔符
    所有路径都变成 /，且不带 . 或 ..
    """
    return os.path.normpath(path).replace('\\', '/')


def convert_to_relative_path(repo_dir, headers) -> list:
    """
    获取头文件相对于仓库的路径
    """
    header_relative_paths = []
    for header in headers:
        header_relative_path = os.path.relpath(header, repo_dir)
        header_relative_path = normalize_path(header_relative_path)
        header_relative_paths.append(header_relative_path)
    return header_relative_paths


def count_headers(abs_include_dirs):
    """
    计算给定目录列表中的头文件数量。

    :param abs_include_dirs: 包含绝对路径的目录列表。
    :return: 头文件数量。
    """
    def count_files_in_dir(directory):
        """
        计算目录中的文件数量，包括子目录中的文件。

        :param directory: 目录路径。
        :return: 文件数量。
        """
        return sum(len(files) for _, _, files in os.walk(directory))

    count = 0
    invalid_dirs = []
    for dir in abs_include_dirs:
        if os.path.isfile(dir):
            count += 1
        elif os.path.isdir(dir):
            count += count_files_in_dir(dir)
        else:
            invalid_dirs.append(dir)

    return count, invalid_dirs


def generate_include_header_regex():
    """
    生成匹配头文件的正则表达式。
    """
    include_pattern = r'#include\s+[<"]([^">]+)[">]'
    return re.compile(include_pattern)


def find_all_headers(file_path, include_dirs) -> Tuple[Set[str], Set[str]]:
    """
    递归查找给定C/C++源文件所包含的所有头文件。
    只处理绝对路径，返回的也都是绝对路径

    :param file_path: C/C++源文件的绝对路径。
    :param include_dirs: 需要搜索头文件的目录列表。
    :return: headers, unexist_headers
    """
    headers = set()
    unexist_headers = set()
    include_pattern = generate_include_header_regex()

    for dir in include_dirs:
        # dir 是文件路径
        if os.path.isfile(dir):
            headers.add(dir)
            continue

    def get_header_path(header_name):
        """
        在指定的目录列表中查找头文件的路径。

        :param header_name: 头文件名。
        :return: 头文件的绝对路径，如果未找到则返回None。
        """
        for dir in include_dirs:
            header_path = os.path.join(dir, header_name)
            if os.path.exists(header_path):
                return os.path.abspath(header_path)
        return None

    def parse_file(file_path):
        """
        解析文件内容，递归处理每个包含的头文件。

        :param file_path: 文件的绝对路径。
        """
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path) or file_path in headers:
            return
        headers.add(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for match in include_pattern.findall(content):
                header_path = get_header_path(match)
                if header_path:
                    parse_file(header_path)
                else:
                    unexist_headers.add(match)

    parse_file(file_path)
    return headers, unexist_headers


def find_src_include_headers(file_path, include_dirs) -> Tuple[Set[str], Set[str]]:
    """
    查找给定C/C++源文件所包含的所有头文件，不进行递归查找。
    只处理绝对路径，返回的也都是绝对路径

    :param file_path: C/C++源文件的绝对路径。
    :param include_dirs: 需要搜索头文件的目录列表。
    :return: 包含所有需要的头文件绝对路径的集合。
    """
    headers = set()
    unexist_headers = set()
    include_pattern = generate_include_header_regex()

    for dir in include_dirs:
        # dir 是文件路径
        if os.path.isfile(dir):
            headers.add(dir)
            continue

    def get_header_path(header_name):
        """
        在指定的目录列表中查找头文件的路径。

        :param header_name: 头文件名。
        :return: 头文件的绝对路径，如果未找到则返回None。
        """
        for dir in include_dirs:
            header_path = os.path.join(dir, header_name)
            if os.path.exists(header_path):
                return os.path.abspath(header_path)
        return None

    file_path = normalize_path(file_path)
    if not os.path.exists(file_path) or file_path in headers:
        return
    headers.add(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        for match in include_pattern.findall(content):
            header_path = get_header_path(match)
            if header_path:
                header_path = normalize_path(header_path)
                headers.add(header_path)
            else:
                unexist_headers.add(match)
    return headers, unexist_headers


def param_process(repo_path, cpp_file_relative_path, include_dirs_relative_pahts):
    # 获取绝对路径
    cpp_file_path = os.path.join(repo_path, cpp_file_relative_path)
    include_dirs = [os.path.join(repo_path, dir)
                    for dir in include_dirs_relative_pahts]

    # 归一化路径
    cpp_file_path = normalize_path(cpp_file_path)
    include_dirs = [normalize_path(dir) for dir in include_dirs]
    return cpp_file_path, include_dirs


def get_abs_headers(repo_path, cpp_file_relative_path, include_dirs_relative_pahts, shouldRecursion=True) -> Tuple[Set[str], Set[str]]:
    cpp_file_path, include_dirs = param_process(
        repo_path, cpp_file_relative_path, include_dirs_relative_pahts)
    if shouldRecursion:
        return find_all_headers(cpp_file_path, include_dirs)
    else:
        return find_src_include_headers(cpp_file_path, include_dirs)


def get_relative_headers(repo_path, cpp_file_relative_path, include_dirs_relative_pahts, shouldRecursion=True) -> Tuple[list[str], list[str]]:
    headers, unexist_headers = get_abs_headers(
        repo_path, cpp_file_relative_path, include_dirs_relative_pahts, shouldRecursion)
    headers = convert_to_relative_path(repo_path, headers)
    return headers, list(unexist_headers)


def get_relative_headers_of_files(repo_path, cpp_files, include_dirs_relative_pahts, shouldRecursion=True) -> Tuple[list[str], list[str]]:
    headers_set = set()
    unexist_headers_set = set()
    for cpp_file in cpp_files:
        headers, unexist_headers = get_relative_headers(
            repo_path, cpp_file, include_dirs_relative_pahts, shouldRecursion)
        headers_set.update(headers)
        unexist_headers_set.update(unexist_headers)
    return list(headers_set), list(unexist_headers_set)


def extract_include_header_changes(diff_text):
    """
    从差异内容中提取修改的头文件
    """
    include_pattern = generate_include_header_regex()
    changes = []

    diff_lines = diff_text.splitlines()
    in_diff = False

    for line in diff_lines:
        if line.startswith('diff --git'):
            in_diff = True
        elif in_diff and (line.startswith('---') or line.startswith('+++')):
            continue
        elif in_diff and (line.startswith('+') or line.startswith('-')):
            include_match = include_pattern.search(line)
            if include_match:
                # 只提取头文件名部分
                header_file = include_match.group(1)
                changes.append(header_file)

    return changes


def get_diff_headers_of_files_all_commits(repo_path, target_files: list) -> list:
    commits = set()
    for target_file in tqdm(target_files, desc="Processing target_files", unit="file"):
        commits.update(get_file_commits(repo_path, target_file))

    headers = set()

    # 使用tqdm显示进度条
    for commit in tqdm(commits, desc="Processing commits", unit="commit"):
        diff_text = get_commit_diff(repo_path, commit)
        include_header_changes = extract_include_header_changes(diff_text)
        headers.update(include_header_changes)

    return list(headers)


def get_relative_headers_of_files_all_commits(repo_path, cpp_files, include_dirs_relative_pahts, shouldRecursion=True, timer: Timer = None) -> list:
    if timer:
        timer.lap()

    headers_set = set()

    # 获取 当前commit 下的所有相关头文件
    headers, unexist_headers = get_relative_headers_of_files(
        repo_path, cpp_files, include_dirs_relative_pahts, shouldRecursion)
    headers_set.update(headers)
    headers_set.update(unexist_headers)
    len_before = len(headers_set)
    print(f"headers: {len(headers)}")
    print(f"unexist_headers: {len(unexist_headers)}")
    print(f"headers_set: {len_before}")
    if timer:
        timer.lap_and_show("get_relative_headers_of_files")

    # 获取 所有commit 下的所有涉及的头文件
    headers_set.update(get_diff_headers_of_files_all_commits(
        repo_path, cpp_files))
    len_after = len(headers_set)
    print(f"headers_set: {len_before} -> {len_after}")
    if timer:
        timer.lap_and_show("get_diff_headers_of_files_all_commits")

    return list(headers_set)


def demo1_recursion():
    repo_path = r'D:\coding\zhurong-CodeWisdom\test_codes\linux-stable\linux-stable'  # 仓库路径
    cpp_file_relative_paths = ['mm/memory.c', 'mm/hugetlb.c']  # 需要解析的C/CPP文件路径
    include_dirs_relative_pahts = [
        './arch/x86/include',
        './arch/x86/include/generated',
        './include',
        './arch/x86/include/uapi',
        './arch/x86/include/generated/uapi',
        './include/uapi',
        './include/generated/uapi',
        './include/linux/compiler-version.h',
        './include/linux/kconfig.h',
        './include/linux/compiler_types.h'
    ]

    cpp_file_path, include_dirs = param_process(
        repo_path, cpp_file_relative_paths[0], include_dirs_relative_pahts)

    headers, _ = get_relative_headers_of_files(
        repo_path, cpp_file_relative_paths, include_dirs_relative_pahts)

    for header in headers:
        print(header)

    print("=======================================================")
    all, invalid_dirs = count_headers(include_dirs)
    print(f"Total/filtered/invalid: {all}/{len(headers)}/{len(invalid_dirs)}")
    print("Invalid directories:")
    for dir in invalid_dirs:
        print(dir)


def demo2_no_recursion():
    repo_path = r'D:\coding\zhurong-CodeWisdom\test_codes\linux-stable\linux-stable'  # 仓库路径
    cpp_file_relative_paths = ['mm/memory.c', 'mm/hugetlb.c']  # 需要解析的C/CPP文件路径
    include_dirs_relative_pahts = [
        './arch/x86/include',
        './arch/x86/include/generated',
        './include',
        './arch/x86/include/uapi',
        './arch/x86/include/generated/uapi',
        './include/uapi',
        './include/generated/uapi',
        './include/linux/compiler-version.h',
        './include/linux/kconfig.h',
        './include/linux/compiler_types.h'
    ]

    cpp_file_path, include_dirs = param_process(
        repo_path, cpp_file_relative_paths[0], include_dirs_relative_pahts)

    headers, _ = get_relative_headers_of_files(
        repo_path, cpp_file_relative_paths, include_dirs_relative_pahts, False)

    for header in headers:
        print(header)

    print("=======================================================")
    all, invalid_dirs = count_headers(include_dirs)
    print(f"Total/filtered/invalid: {all}/{len(headers)}/{len(invalid_dirs)}")
    print("Invalid directories:")
    for dir in invalid_dirs:
        print(dir)


def demo3_all_commits_recursion():
    repo_path = r'D:\coding\zhurong-CodeWisdom\test_codes\linux-stable\linux-stable'
    cpp_file_relative_paths = ['mm/memory.c', 'mm/hugetlb.c']  # 需要解析的C/CPP文件路径
    include_dirs_relative_pahts = [
        './arch/x86/include',
        './arch/x86/include/generated',
        './include',
        './arch/x86/include/uapi',
        './arch/x86/include/generated/uapi',
        './include/uapi',
        './include/generated/uapi',
        './include/linux/compiler-version.h',
        './include/linux/kconfig.h',
        './include/linux/compiler_types.h'
    ]

    cpp_file_path, include_dirs = param_process(
        repo_path, cpp_file_relative_paths[0], include_dirs_relative_pahts)

    headers = get_relative_headers_of_files_all_commits(
        repo_path, cpp_file_relative_paths, include_dirs_relative_pahts, True)

    for header in headers:
        print(header)

    print("=======================================================")
    all, invalid_dirs = count_headers(include_dirs)
    print(f"Total/filtered/invalid: {all}/{len(headers)}/{len(invalid_dirs)}")
    print("Invalid directories:")
    for dir in invalid_dirs:
        print(dir)
