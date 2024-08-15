from common.GitFilesFilter import statistics_split_info
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Show the earliest commit time of a Git repository.')
    parser.add_argument('-r', '--repo', required=True,
                        help='The path to the Git repository.')
    parser.add_argument('-tf', '--target_files', nargs='+',
                        required=False, default=[], help='The target files to be counted.')
    args = parser.parse_args()
    repo_path = args.repo
    cpp_file_relative_paths = args.target_files
    print('repo_path:', repo_path)
    print('cpp_file_relative_paths:', cpp_file_relative_paths)
    statistics_split_info(repo_path, cpp_file_relative_paths)
