from common.GitFilesFilter import split_cpp_modules


def main():
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
    modules = ['mm']
    new_repo_name = 'linux-split-mm-1'
    new_repo_location = r"/home/app/repository"
    new_branch_name = 'demo'
    track_gitignore = True
    regex_with_glob = False

    split_cpp_modules(repo_path=repo_path,
                    include_dirs_relative_pahts=include_dirs_relative_pahts,
                    modules=modules,
                    new_repo_name=new_repo_name,
                    new_repo_location=new_repo_location,
                    new_branch_name=new_branch_name,
                    track_gitignore=track_gitignore,
                    timer=None,
                    regex_with_glob=regex_with_glob)


if __name__ == "__main__":
    main()
