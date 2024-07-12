import os
import sys
import subprocess
import argparse
import time
from common.GitUtils import add_virtual_remote, delete_branch, show_commit_count, show_earliest_commit_time


def split_module(original_repo_path, module_path, new_repo_name, new_repo_location):
    # 检查原始仓库是否存在
    if not os.path.isdir(os.path.join(original_repo_path, ".git")):
        print(
            f"Error: The path {original_repo_path} does not appear to be a Git repository.")
        sys.exit(1)

    # 导航到原始仓库
    os.chdir(original_repo_path)

    # 使用 git subtree split 提取指定模块的历史记录并创建新分支
    temp_branch = new_repo_name + '-branch'
    subprocess.run(['git', 'subtree', 'split', '--prefix=' +
                   module_path, '-b', temp_branch, '--rejoin'], check=True)

    # 创建新的仓库
    new_repo_path = os.path.join(new_repo_location, new_repo_name)
    os.makedirs(new_repo_path, exist_ok=True)
    os.chdir(new_repo_path)
    subprocess.run(['git', 'init'], check=True)

    # 将拆分的分支拉取到新的仓库中
    subprocess.run(
        ['git', 'pull', original_repo_path, temp_branch], check=True)

    # 为新仓库添加虚拟远程仓库
    add_virtual_remote(new_repo_name)

    # 回到原始仓库并删除临时分支
    os.chdir(original_repo_path)
    delete_branch(temp_branch)
    print("========================处理完成========================")
    print(
        f"Module {module_path} has been successfully split into a new repository at {new_repo_path}.")
    # 展示提交数
    show_commit_count()
    # 展示最早的提交时间
    show_earliest_commit_time()


if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Split a module from a Git repository into a new repository.")
    parser.add_argument("-o", "--original_repo_path", required=True,
                        help="Path to the original Git repository.")
    parser.add_argument("-m", "--module_path", required=True,
                        help="Path to the module within the original repository.")
    parser.add_argument("-nn", "--new_repo_name",
                        required=True, help="Name of the new repository.")
    parser.add_argument("-nl", "--new_repo_location", required=True,
                        help="Location where the new repository will be created.")

    args = parser.parse_args()

    try:
        split_module(args.original_repo_path, args.module_path,
                     args.new_repo_name, args.new_repo_location)
    except Exception as e:
        print(f"Error: {e}")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
