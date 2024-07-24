from common.GitUtils import get_files_commits

cpp_file_relative_paths = ['mm/memory.c', 'mm/hugetlb.c']  # 需要解析的C/CPP文件路径


def get_commits(repo_path):
    return get_files_commits(repo_path, cpp_file_relative_paths)


if __name__ == '__main__':
    linux_stable_repo_path = r'/mnt/d/coding/zhurong-CodeWisdom/test_codes/linux-stable/linux-stable'
    linux_stable_clean_repo_path = r'/mnt/d/coding/zhurong-CodeWisdom/test_codes/linux-stable/linux-stable-clean'

    linux_stable_commits = get_commits(linux_stable_repo_path)
    linux_stable_clean_commits = get_commits(linux_stable_clean_repo_path)

    print(f"linux-stable commits: {len(linux_stable_commits)}")
    print(f"linux-stable-clean commits: {len(linux_stable_clean_commits)}")

    common_commits = set(linux_stable_commits) & set(linux_stable_clean_commits)
    print(f"common commits: {len(common_commits)}")
    print(f"common commits: {common_commits}")
    
    different_commits = set(linux_stable_commits) - set(linux_stable_clean_commits)
    print(f"different commits: {len(different_commits)}")
    print(f"different commits: {different_commits}")
     
