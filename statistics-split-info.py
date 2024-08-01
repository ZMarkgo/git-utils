from common.GitUtils import show_commit_count, show_count_files_commits, show_earliest_commit_time
from common.FileUtils import show_count_file_ext
from common.TimeUtils import Timer
from common.PrintUtils import print_sep
import argparse

if __name__ == '__main__':
    timer = Timer()
    parser = argparse.ArgumentParser(
        description='Show the earliest commit time of a Git repository.')
    parser.add_argument('-r', '--repo', required=True,
                        help='The path to the Git repository.')
    args = parser.parse_args()
    repo_path = args.repo

    print_sep('count files')
    timer.lap()
    show_count_file_ext(repo_path, '.c')
    show_count_file_ext(repo_path, '.h')
    timer.lap_and_show('Counting .c and .h files')

    print_sep('count all commits')
    timer.lap()
    show_commit_count(repo_path)
    timer.lap_and_show('Counting all commits')

    print_sep('count commits of target files')
    timer.lap()
    cpp_file_relative_paths = ['mm/memory.c']
    show_count_files_commits(repo_path, cpp_file_relative_paths)
    timer.lap_and_show('Counting commits of target files')

    print_sep('show earliest commit time')
    timer.lap()
    show_earliest_commit_time(repo_path)
    timer.lap_and_show('Showing earliest commit time')

    timer.end()
    timer.show_time_cost()