import os
import shutil
import subprocess
import datetime

# 结尾不带斜杠
ORIGIN_REPO_BASE_URL = "http://fdse.gitlab.com/platform"


def copy_dir(src, dest):
    """
    复制目录到指定位置并重命名。

    :param src: 源目录路径
    :param dest: 目标目录路径
    """
    # 如果是Linux系统
    if os.name == 'posix':
        result = subprocess.run(['cp', '-r', src, dest],
                                capture_output=True, text=True)
    else:
        # 确保目标目录的父目录存在
        dest_parent_dir = os.path.dirname(dest)
        if not os.path.exists(dest_parent_dir):
            os.makedirs(dest_parent_dir)

        # 使用robocopy进行目录复制
        # /E 复制所有子目录，包括空的
        # /COPY:DAT 复制文件数据、属性和时间戳
        # /R:0 不重试失败的复制
        result = subprocess.run(
            ['robocopy', src, dest, '/E', '/COPY:DAT', '/R:0'], capture_output=True, text=True)

    # 处理结果
    if result.returncode != 0:
        print(
            f"Error: Command returned non-zero exit status {result.returncode}.")
        print("Error:", result.stderr)
    else:
        print("Command executed successfully.")


def remove_dir(path):
    """
    删除指定目录及其内容。

    :param path: 要删除的目录路径
    """
    if os.path.exists(path) and os.path.isdir(path):
        # 如果是linux系统
        if os.name == 'posix':
            subprocess.run(['rm', '-rf', path], check=True)
        else:
            shutil.rmtree(path)
    else:
        print(f"路径 {path} 不存在或不是一个目录。")


def list_gitignore_files(repo_path):
    """
    返回所有 .gitignore 文件相对于仓库根目录的路径。

    :param repo_path: 仓库根目录路径
    :return: 包含所有 .gitignore 文件路径的列表
    """
    # 获取当前工作目录
    current_dir = os.getcwd()

    try:
        # 切换到仓库目录
        os.chdir(repo_path)

        # 使用 git ls-files 列出所有文件，并使用 grep 筛选出 .gitignore 文件
        result = subprocess.run(
            ['git', 'ls-files', '*.gitignore'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )

        # 分割结果为行，并返回列表
        gitignore_files = result.stdout.splitlines()

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        gitignore_files = []

    finally:
        # 切换回原始工作目录
        os.chdir(current_dir)

    return gitignore_files


def get_git_remotes():
    # 获取当前Git仓库中的所有远程仓库
    result = subprocess.run(
        ['git', 'remote'], stdout=subprocess.PIPE, universal_newlines=True)
    remotes = result.stdout.split()
    return remotes


def remove_git_remote(remote_name):
    # 删除指定名称的远程仓库
    subprocess.run(['git', 'remote', 'remove', remote_name])


def remove_all_git_remotes():
    # 获取所有远程仓库并删除它们
    remotes = get_git_remotes()
    for remote in remotes:
        remove_git_remote(remote)
        print(f'Remote "{remote}" has been removed.')


def add_remote(origin_repo_url):
    """
    为仓库添加远程仓库
    """
    subprocess.run(['git', 'remote', 'add', 'origin',
                   origin_repo_url], check=True)


def add_virtual_remote(new_repo_name):
    """
    为新仓库添加虚拟远程仓库
    """
    origin_repo_url = f"{ORIGIN_REPO_BASE_URL}/{new_repo_name}.git"
    print(f"Virtual origin repo URL: {origin_repo_url}")
    add_remote(origin_repo_url)


def create_branch(new_branch_name):
    subprocess.run(['git', 'checkout', '-b', new_branch_name], check=True)


def delete_branch(branch_name):
    subprocess.run(['git', 'branch', '-D', branch_name], check=True)


def get_commit_count(repo_path='.'):
    """
    获取项目中的提交数 
    git rev-list --count HEAD
    """
    working_dir = os.getcwd()
    os.chdir(repo_path)
    result = subprocess.run(
        ['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE)
    os.chdir(working_dir)
    return result.stdout.decode('utf-8')


def get_all_commits(repo_path='.') -> list:
    """
    获取所有提交记录
    """
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H'],
        capture_output=True,
        text=True,
        check=True
    )

    # 提交记录以换行符分隔
    commits = result.stdout.strip().split('\n')

    return commits


def get_file_commits(repo_path, file_relative_path) -> list:
    """
    获取文件的提交记录
    """
    # 使用git log命令获取文件的提交记录
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H', file_relative_path],
        capture_output=True,
        text=True,
        check=True
    )

    # 提交记录以换行符分隔
    commits = result.stdout.strip().split('\n')

    return commits


def count_file_commits(repo_path, file_relative_path):
    """
    获取文件的提交记录
    """
    return len(get_file_commits(repo_path, file_relative_path))


def get_files_commits(repo_path, file_relative_paths) -> list:
    """
    获取多个文件的提交记录
    """
    commits = set()
    for file_relative_path in file_relative_paths:
        commits.update(get_file_commits(repo_path, file_relative_path))
    return list(commits)


def count_files_commits(repo_path, file_relative_paths):
    """
    获取多个文件的提交记录
    """
    return len(get_files_commits(repo_path, file_relative_paths))


def format_count_files_commits_msg(repo_path, file_relative_paths):
    """
    统计并格式化多个文件的提交记录信息
    :param repo_path: 仓库路径
    :param file_relative_paths: 文件相对路径列表
    """
    commits_count = count_files_commits(repo_path, file_relative_paths)
    return f"Commits count of {file_relative_paths}: \n\t{commits_count}"


def show_count_files_commits(repo_path, file_relative_paths):
    """
    显示多个文件的提交记录信息
    :param repo_path: 仓库路径
    :param file_relative_paths: 文件相对路径列表
    """
    print(format_count_files_commits_msg(repo_path, file_relative_paths))


def checkout_commit(repo_path, commit_hash):
    """
    检出指定的提交
    :param repo_path: 仓库路径
    :param commit_hash: 提交哈希
    :return: 如果检出成功则返回True，否则返回False
    """
    try:
        # 使用git checkout命令检出指定的提交
        subprocess.run(
            ['git', '-C', repo_path, 'checkout', commit_hash], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


def get_commit_message(repo_path, commit_hash):
    """
    获取指定提交的提交信息
    :param repo_path: 仓库路径
    :param commit_hash: 提交哈希
    :return: 提交信息，如果失败则返回None
    """
    try:
        # 使用git log命令获取提交信息
        result = subprocess.run(
            ['git', '-C', repo_path, 'log', '--format=%B', '-n', '1', commit_hash],
            capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def get_commit_files(repo_path, commit_hash) -> list:
    """
    获取指定提交修改的文件
    :param repo_path: 仓库路径
    :param commit_hash: 提交哈希
    :return: 修改的文件列表
    """
    result = subprocess.run(
        ['git', '-C', repo_path, 'show', '--name-only',
            '--pretty=format:', commit_hash],
        stdout=subprocess.PIPE, text=True
    )
    return result.stdout.splitlines()


def format_get_commit_count_msg(repo_path='.'):
    """
    获取并格式化提交数量信息
    """
    commit_count = get_commit_count(repo_path=repo_path)
    return f"Commit count: {commit_count}"


def show_commit_count(repo_path='.'):
    """
    显示提交数量信息
    """
    print(format_get_commit_count_msg(repo_path=repo_path))


def get_commit_diff(repo_path, commit_hash):
    """
    获取指定提交的差异内容
    """
    try:
        result = subprocess.run(['git', '-C', repo_path, 'show', commit_hash], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                errors='replace')
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return None


class RepoSizeInfo:
    """
    size: 0
    in-pack: 65
    packs: 1
    size-pack: 9
    prune-packable: 0
    garbage: 0
    size-garbage: 0
    """

    def __init__(self, size, in_pack, packs, size_pack, prune_packable, garbage, size_garbage):
        self.size = size
        self.in_pack = in_pack
        self.packs = packs
        self.size_pack = size_pack
        self.prune_packable = prune_packable
        self.garbage = garbage
        self.size_garbage = size_garbage

    def __str__(self):
        return f"size: {self.size}\n" \
               f"in-pack: {self.in_pack}\n" \
               f"packs: {self.packs}\n" \
               f"size-pack: {self.size_pack}\n" \
               f"prune-packable: {self.prune_packable}\n" \
               f"garbage: {self.garbage}\n" \
               f"size-garbage: {self.size_garbage}"


def get_repo_size_change_info(before: RepoSizeInfo, after: RepoSizeInfo) -> str:
    return \
        f"size: {before.size} -> {after.size}\n" \
        f"in-pack: {before.in_pack} -> {after.in_pack}\n" \
        f"packs: {before.packs} -> {after.packs}\n" \
        f"size-pack: {before.size_pack} -> {after.size_pack}\n" \
        f"prune-packable: {before.prune_packable} -> {after.prune_packable}\n" \
        f"garbage: {before.garbage} -> {after.garbage}\n" \
        f"size-garbage: {before.size_garbage} -> {after.size_garbage}"


def get_repo_size_info() -> RepoSizeInfo:
    """
    获取仓库的大小信息 git count-objects -v
    """
    result = subprocess.run(
        ['git', 'count-objects', '-v'], stdout=subprocess.PIPE)
    repo_size = result.stdout.decode('utf-8').split('\n')
    # 提取信息
    size = int(repo_size[0].split(': ')[1])
    in_pack = int(repo_size[1].split(': ')[1])
    packs = int(repo_size[2].split(': ')[1])
    size_pack = int(repo_size[3].split(': ')[1])
    prune_packable = int(repo_size[4].split(': ')[1])
    garbage = int(repo_size[5].split(': ')[1])
    size_garbage = int(repo_size[6].split(': ')[1])
    return RepoSizeInfo(size, in_pack, packs, size_pack, prune_packable, garbage, size_garbage)


def show_repo_size_info():
    repo_size = get_repo_size_info()
    print(repo_size)


def get_earliest_commit_date(repo_path):
    """
    获取仓库最早提交时间的函数（通用版本）
    """
    # Navigate to the repository path
    command = ["git", "-C", repo_path, "log",
               "--reverse", "--pretty=format:%ci"]

    # Execute the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True)

    # Check if there was an error
    if result.returncode != 0:
        raise Exception(f"Error running git command: {result.stderr.strip()}")

    # Get the output, which is the list of commit dates
    commit_dates = result.stdout.strip().split('\n')

    # The first date in the list is the earliest commit date
    earliest_commit_date_str = commit_dates[0]

    # Convert the date string to a datetime object
    earliest_commit_date = datetime.datetime.strptime(
        earliest_commit_date_str, "%Y-%m-%d %H:%M:%S %z")

    return earliest_commit_date


def format_get_earliest_commit_date_msg(repo_path='.'):
    """
    获取并格式化仓库最早提交时间信息
    """
    earliest_commit_date = get_earliest_commit_date(repo_path=repo_path)
    return f"Earliest commit date: {earliest_commit_date}"


def show_earliest_commit_time(repo_path='.'):
    """
    展示仓库最早的提交时间 
    """
    print(format_get_earliest_commit_date_msg(repo_path=repo_path))
