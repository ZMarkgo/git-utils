from common.TimeUtils import Timer
from common.GitFilesFilter import split_files
from common.CppHeaderUtils import get_relative_headers_of_files


if __name__ == "__main__":
    timer = Timer()
    repo_path = r'D:\coding\zhurong-CodeWisdom\test_codes\linux-stable\linux-stable'  # 仓库路径
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

    target_paths = ['mm/memory.c', 'mm/hugetlb.c']
    headers = get_relative_headers_of_files(
        repo_path, target_paths, include_dirs_relative_pahts)
    target_paths.extend(headers)

    new_repo_name = 'linux-stable-split-demo3'
    new_repo_location = r"D:\coding\zhurong-CodeWisdom\test_codes"
    new_branch_name = 'demo3'
    track_gitignore = False

    try:
        split_files(original_repo_path=repo_path,
                    target_paths=target_paths,
                    new_repo_name=new_repo_name,
                    new_repo_location=new_repo_location,
                    new_branch_name=new_branch_name,
                    track_gitignore=track_gitignore)
    except Exception as e:
        print(f"Error: {e}")

    timer.end()
    timer.show_time_cost()