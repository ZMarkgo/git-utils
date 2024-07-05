import os
import sys
import subprocess
import argparse
from TimeUtils import Timer
from utils import copy_dir, remove_dir, list_gitignore_files, show_repo_size_info, remove_all_git_remotes, add_virtual_remote, create_branch, show_commit_count, show_earliest_commit_time

def split_files(original_repo_path="", target_files: list = [], new_repo_name="", new_repo_location="", new_branch_name=""):
    # 检查原始仓库是否存在
    if not os.path.isdir(os.path.join(original_repo_path, ".git")):
        print(
            f"Error: The path {original_repo_path} does not appear to be a Git repository.")
        sys.exit(1)
    # 检查list是否为空
    if not target_files:
        print("Error: The target_files list is empty.")
        sys.exit(1)
    # 检查新仓库名称是否为空
    if not new_repo_name:
        print("Error: The new_repo_name is empty.")
        sys.exit(1)
    # 检查新仓库位置是否存在
    if not os.path.isdir(new_repo_location):
        print(f"Error: The path {new_repo_location} does not exist.")
        sys.exit(1)
    # 检查新分支名称是否为空字符串
    if not new_branch_name:
        print("Error: The new_branch_name is empty.")
        sys.exit(1)

    print("========================复制仓库========================")
    # 复制原始仓库到新的位置
    new_repo_path = os.path.join(new_repo_location, new_repo_name)
    print(f"Original repo path: {original_repo_path}")
    print(f"New repo location: {new_repo_path}")
    copy_dir(original_repo_path, new_repo_path)

    # 切换到仓库
    os.chdir(new_repo_path)

    print("========================提取文件及其历史========================")
    # 使用 git filter-repo 提取指定文件的历史记录
    split_cmd = ['git', 'filter-repo']
    for target_file in target_files:
        split_cmd.extend(['--path', target_file])
    # 保留所有 gitignore 文件
    gitignore_files = list_gitignore_files(new_repo_path)
    for gitignore_file in gitignore_files:
        split_cmd.extend(['--path', gitignore_file])
    split_cmd.extend(['--force'])
    # split_cmd.extend(['--reencode=yes'])
    subprocess.run(split_cmd, check=True)

    # 仓库瘦身
    print("========================仓库瘦身========================")
    print("Before:")
    show_repo_size_info()
    # 移除 filter-repo 残留数据
    remove_dir('.git/filter-repo')
    # 清理未使用的对象
    # git reflog expire --expire=now --all && git gc --prune=now --aggressive
    subprocess.run(['git', 'reflog', 'expire',
                   '--expire=now', '--all'], check=True)
    subprocess.run(['git', 'gc', '--prune=now', '--aggressive'], check=True)
    print("After:")
    show_repo_size_info()

    # 为新仓库添加虚拟远程仓库
    print("========================添加虚拟远程仓库========================")
    remove_all_git_remotes()
    add_virtual_remote(new_repo_name)

    # 创建新分支
    print("========================创建新分支========================")
    print(f"New branch name: {new_branch_name}")
    create_branch(new_branch_name)

    print("========================处理完成========================")
    # 展示提交数
    show_commit_count()
    # 展示最早的提交时间
    show_earliest_commit_time()


if __name__ == "__main__":
    timer = Timer()
    parser = argparse.ArgumentParser(
        description="Split several files from a Git repository into a new repository.")
    parser.add_argument("-o", "--original_repo_path", required=True,
                        help="Path to the original Git repository.")
    parser.add_argument("-tfs", "--target_files", nargs='+',
                        required=True, help="List of target files to be split.")
    parser.add_argument("-nn", "--new_repo_name",
                        required=True, help="Name of the new repository.")
    parser.add_argument("-nl", "--new_repo_location", required=True,
                        help="Location where the new repository will be created.")
    parser.add_argument("-nb", "--new_branch_name",
                        required=True, help="Name of the new branch.")
    args = parser.parse_args()

    original_repo_path = args.original_repo_path
    target_files = args.target_files
    new_repo_name = args.new_repo_name
    new_repo_location = args.new_repo_location
    new_branch_name = args.new_branch_name

    try:
        split_files(original_repo_path=original_repo_path,
                    target_files=target_files,
                    new_repo_name=new_repo_name,
                    new_repo_location=new_repo_location,
                    new_branch_name=new_branch_name)
    except Exception as e:
        print(f"Error: {e}")

    timer.end()
    timer.show_time_cost()