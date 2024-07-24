from common.GitUtils import get_files_commits, get_all_commits, get_commit_message, get_commit_files

cpp_file_relative_paths = ['mm/memory.c', 'mm/hugetlb.c']  # 需要解析的C/CPP文件路径


if __name__ == '__main__':
    repo_path = r'/mnt/d/coding/zhurong-CodeWisdom/test_codes/linux-stable-split-demo2-no-h'

    files_commits = get_files_commits(repo_path, cpp_file_relative_paths)
    all_commits = get_all_commits(repo_path=repo_path)

    set_files_commits = set(files_commits)
    set_all_commits = set(all_commits)

    print(f"files_commits: {len(files_commits)}")
    print(f"all_commits: {len(all_commits)}")

    print(f"set_files_commits: {len(set_files_commits)}")
    print(f"set_all_commits: {len(set_all_commits)}")

    same_commits = set_files_commits & set_all_commits
    print(f"same_commits: {len(same_commits)}")

    different_commits = set_all_commits - set_files_commits
    print(f"different_commits: {len(different_commits)}")
    none_commits = []
    merge_commits = []
    un_match_commits = []
    for commit in different_commits:
        msg = get_commit_message(repo_path, commit)
        files = get_commit_files(repo_path, commit)
        # msg 是否包含 "Merge" 字符串
        commit_content = {
            "commit": commit,
            "files": files,
            "msg": msg
        }
        if msg is None:
            none_commits.append(commit_content)
        elif "Merge" in msg:
            merge_commits.append(commit_content)
        else:
            un_match_commits.append(commit_content)

    print(f"total different_commits: {len(different_commits)}")
    print(f"none_commits: {len(none_commits)}")
    print(f"merge_commits: {len(merge_commits)}")
    print(f"un_match_commits: {len(un_match_commits)}")
    print("none_commits:")
    for none_commit in none_commits:
        print(none_commit)
    print("merge_commits:")
    for merge_commit in merge_commits:
        print(merge_commit)
    print("un_match_commits:")
    for un_match_commit in un_match_commits:
        print(un_match_commit)