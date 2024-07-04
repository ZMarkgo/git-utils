from utils import show_commit_count
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Show the number of commits in the Git repository.')
    parser.add_argument('-r', '--repo', required=True,
                        help='The path to the Git repository.')
    args = parser.parse_args()
    if args.repo:
        show_commit_count(args.repo)
