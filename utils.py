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
    # 如果是linux系统
    if os.name == 'posix':
        subprocess.run(['cp', '-r', src, dest], check=True)
    else:
        # 确保目标目录的父目录存在
        dest_parent_dir = os.path.dirname(dest)
        if not os.path.exists(dest_parent_dir):
            os.makedirs(dest_parent_dir)
        # 复制目录
        shutil.copytree(src, dest)


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


def show_commit_count(repo_path='.'):
    commit_count = get_commit_count(repo_path=repo_path)
    print(f"Commit count: {commit_count}")


def get_repo_size():
    """
    获取仓库的大小信息 git count-objects -v
    """
    result = subprocess.run(
        ['git', 'count-objects', '-v'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def show_repo_size_info():
    repo_size = get_repo_size()
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


def show_earliest_commit_time():
    """
    展示仓库最早的提交时间 
    git show -s --format=%ci $(git rev-list --max-parents=0 HEAD)
    """
    # 如果是linux系统
    if os.name == 'posix':
        subprocess.run(['git', 'show', '-s', '--format=%ci',
                       '$(git', 'rev-list', '--max-parents=0', 'HEAD)'], check=True)
    else:
        earliest_commit_date = get_earliest_commit_date('.')
        print(f"Earliest commit date: {earliest_commit_date}")
