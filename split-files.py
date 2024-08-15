import argparse
from common.Timer import Timer
from common.GitFilesFilter import split_files


if __name__ == "__main__":
    timer = Timer()
    parser = argparse.ArgumentParser(
        description="Split several files from a Git repository into a new repository.")
    parser.add_argument("-o", "--original_repo_path", required=True,
                        help="Path to the original Git repository.")
    parser.add_argument("-tps", "--target_paths", nargs='+',
                        required=True, help="List of target files to be split.")
    parser.add_argument("-nn", "--new_repo_name",
                        required=True, help="Name of the new repository.")
    parser.add_argument("-nl", "--new_repo_location", required=True,
                        help="Location where the new repository will be created.")
    parser.add_argument("-nb", "--new_branch_name",
                        required=True, help="Name of the new branch.")
    # 是否跟踪 .gitignore 文件
    parser.add_argument("-ig", "--track_gitignore", action='store_true', default=False,
                        help="Track .gitignore files.")
    args = parser.parse_args()

    original_repo_path = args.original_repo_path
    target_paths = args.target_paths
    new_repo_name = args.new_repo_name
    new_repo_location = args.new_repo_location
    new_branch_name = args.new_branch_name
    track_gitignore = args.track_gitignore

    try:
        split_files(original_repo_path=original_repo_path,
                    target_paths=target_paths,
                    new_repo_name=new_repo_name,
                    new_repo_location=new_repo_location,
                    new_branch_name=new_branch_name,
                    track_gitignore=track_gitignore)
    except Exception as e:
        print(f"Error: {e}")

    timer.end()
    timer.show_time_cost()