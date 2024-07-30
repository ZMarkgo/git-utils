from common.GitUtils import count_files_commits

if __name__ == '__main__':
    repo_path = r'/mnt/d/coding/zhurong-CodeWisdom/test_codes/linux-stable/linux-stable'
    cpp_file_relative_paths = ['mm/memory.c', 'mm/hugetlb.c']  # 需要解析的C/CPP文件路径

    commits = count_files_commits(repo_path, cpp_file_relative_paths)
    print(commits)