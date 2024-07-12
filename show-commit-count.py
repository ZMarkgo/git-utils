from common.GitUtils import show_commit_count
import argparse
from common.TimeUtils import Timer

if __name__ == '__main__':
    timer = Timer()
    parser = argparse.ArgumentParser(
        description='Show the number of commits in the Git repository.')
    parser.add_argument('-r', '--repo', required=True,
                        help='The path to the Git repository.')
    args = parser.parse_args()
    
    if args.repo:
        show_commit_count(args.repo)

    timer.end()
    timer.show_time_cost()