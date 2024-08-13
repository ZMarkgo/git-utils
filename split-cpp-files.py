from common.TimeUtils import Timer
from common.GitFilesFilter import split_files, statistics_split_info
from common.CppHeaderUtils import get_relative_headers_of_files, get_relative_headers_of_files_all_commits
import traceback


def main():
    timer = Timer()
    repo_path = r'/home/app/repository/linux'
    # TODO 不同的提取可能需要不同的头文件路径
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
    target_paths = ['mm/memory-failure.c']
    target_c_files = target_paths.copy()
    new_repo_name = 'linux-split-memory-failure-careful-headers-all-gitignore-3'
    new_repo_location = r"/home/app/repository"
    new_branch_name = 'demo'
    track_gitignore = True

    try:
        timer.lap()
        # headers = get_relative_headers_of_files_all_commits(
        #     repo_path, target_paths, include_dirs_relative_pahts,
        #     shouldRecursion=True, timer=timer)
        headers, _ = get_relative_headers_of_files(
            repo_path, target_paths, include_dirs_relative_pahts,
            shouldRecursion=True)
        target_paths.extend(headers)
        print(f"target file or dir num: {len(target_paths)}")
        timer.show_time_cost("Get headers")

        split_files(original_repo_path=repo_path,
                    target_paths=target_paths,
                    new_repo_name=new_repo_name,
                    new_repo_location=new_repo_location,
                    new_branch_name=new_branch_name,
                    track_gitignore=track_gitignore,
                    timer=timer,
                    regex_with_glob=False)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        timer.end()
        timer.show_time_cost()

    try:
        new_repo_path = f"{new_repo_location}/{new_repo_name}"
        statistics_split_info(new_repo_path, target_c_files, timer=Timer())
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
