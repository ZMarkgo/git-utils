from common.GitFilesFilter import split_cpp_modules
from common.Logger import LoggerFactory, LogMetaInfo

# 日志配置信息
LOG_META_INFO = LogMetaInfo(__file__)


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
    new_repo_name = 'linux-split-mm-2'
    new_repo_location = r"/home/app/repository"
    new_branch_name = 'demo'
    track_gitignore = True
    regex_with_glob = False
    start_date = '2021-01-01'
    end_date = LOG_META_INFO.get_date_now()

    LoggerFactory.main_set_log_file_path(
        LOG_META_INFO.get_log_file_path(file_suffix=new_repo_name))
    with LoggerFactory.create_logger(tag=LOG_META_INFO.get_file_tag()) as logger:
        logger.info_print("Start to split cpp modules.")
        split_cpp_modules(repo_path=repo_path,
                          include_dirs_relative_pahts=include_dirs_relative_pahts,
                          modules=modules,
                          new_repo_name=new_repo_name,
                          new_repo_location=new_repo_location,
                          new_branch_name=new_branch_name,
                          track_gitignore=track_gitignore,
                          regex_with_glob=regex_with_glob,
                          start_date=start_date,
                          end_date=end_date)


if __name__ == "__main__":
    main()
