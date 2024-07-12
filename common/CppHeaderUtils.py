import os
import re


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


def find_headers(file_path, include_dirs):
    """
    递归查找给定C/C++源文件所包含的所有头文件。
    只处理绝对路径，返回的也都是绝对路径

    :param file_path: C/C++源文件的绝对路径。
    :param include_dirs: 需要搜索头文件的目录列表。
    :return: 包含所有需要的头文件绝对路径的集合。
    """
    headers = set()
    include_pattern = re.compile(r'#include\s+[<"]([^">]+)[">]')

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

    parse_file(file_path)
    return headers

# 参数处理


def param_process(repo_path, cpp_file_relative_path, include_dirs_relative_pahts):
    # 获取绝对路径
    cpp_file_path = os.path.join(repo_path, cpp_file_relative_path)
    include_dirs = [os.path.join(repo_path, dir)
                    for dir in include_dirs_relative_pahts]

    # 归一化路径
    cpp_file_path = normalize_path(cpp_file_path)
    include_dirs = [normalize_path(dir) for dir in include_dirs]
    return cpp_file_path, include_dirs


def get_abs_headers(repo_path, cpp_file_relative_path, include_dirs_relative_pahts):
    cpp_file_path, include_dirs = param_process(
        repo_path, cpp_file_relative_path, include_dirs_relative_pahts)

    headers = find_headers(cpp_file_path, include_dirs)
    return headers


def get_relative_headers(repo_path, cpp_file_relative_path, include_dirs_relative_pahts):
    headers = get_abs_headers(
        repo_path, cpp_file_relative_path, include_dirs_relative_pahts)
    headers = convert_to_relative_path(repo_path, headers)
    return headers


def get_relative_headers_of_files(repo_path, cpp_files, include_dirs_relative_pahts) -> list:
    headers = set()
    for cpp_file in cpp_files:
        headers.update(get_relative_headers(
            repo_path, cpp_file, include_dirs_relative_pahts))
    return list(headers)


def main():
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

    headers = get_relative_headers_of_files(
        repo_path, cpp_file_relative_paths, include_dirs_relative_pahts)

    for header in headers:
        print(header)

    print("=======================================================")
    all, invalid_dirs = count_headers(include_dirs)
    print(f"Total/filtered/invalid: {all}/{len(headers)}/{len(invalid_dirs)}")
    print("Invalid directories:")
    for dir in invalid_dirs:
        print(dir)


if __name__ == "__main__":
    main()
