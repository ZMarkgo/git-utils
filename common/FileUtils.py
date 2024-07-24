import os


def count_file_ext(repo_path=".", file_extension=".c"):
    """
    统计指定文件类型的文件数量
    :param repo_path: 仓库路径
    :param file_extension: 文件扩展名，如 .c .h
    """
    count = 0

    # POSIX系统 (Linux, macOS)
    if os.name == 'posix':
        result = os.popen(
            f'find {repo_path} -name "*{file_extension}" | wc -l')
        count = result.read().strip()
    # 非POSIX系统 (Windows)
    else:
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(file_extension):
                    count += 1
    return count


def show_count_file_ext(repo_path=".", file_extension=".c"):
    """
    显示指定文件类型的文件数量
    :param repo_path: 仓库路径
    :param file_extension: 文件扩展名，如 .c .h
    """
    count = count_file_ext(repo_path, file_extension)
    print(f'Count of {file_extension} files: {count}')