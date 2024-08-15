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


def count_all_file_ext(repo_path="."):
    """
    统计指定路径下的每种类型（以文件拓展名来区分）的文件数量
    :param repo_path: 仓库路径
    :return: 每种类型（以文件拓展名来区分）的文件数量
    """
    count = {}
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_extension = os.path.splitext(file)[1]
            if file_extension in count:
                count[file_extension] += 1
            else:
                count[file_extension] = 1
    return count


def format_file_ext_count_msg(file_ext: str, count: int):
    """
    格式化指定文件类型的文件数量信息
    :param file_ext: 文件拓展名
    :param count: 文件数量
    :return: 格式化后的文件数量信息
    """
    return f'Count of {file_ext} files: {count}'


def format_count_file_ext_msg(repo_path=".", file_extension=".c"):
    """
    统计指定文件类型的文件数量信息，返回格式化后的信息
    :param repo_path: 仓库路径
    :param file_extension: 文件扩展名，如 .c .h
    """
    count = count_file_ext(repo_path, file_extension)
    return format_file_ext_count_msg(file_extension, count)


def show_count_file_ext(repo_path=".", file_extension=".c"):
    """
    显示指定文件类型的文件数量
    :param repo_path: 仓库路径
    :param file_extension: 文件扩展名，如 .c .h
    """
    print(format_count_file_ext_msg(repo_path, file_extension))


def remove_prefix_slash_and_dot(path: str):
    """
    递归删除前置 '/' 和 './'
    :param path: 路径
    :return: 删除前置 '/' 和 './' 后的路径
    """
    if path.startswith('/'):
        return remove_prefix_slash_and_dot(path[1:])
    if path.startswith('./'):
        return remove_prefix_slash_and_dot(path[2:])
    return path
