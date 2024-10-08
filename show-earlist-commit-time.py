from common.GitUtils import show_earliest_commit_time
import argparse
from common.Timer import Timer

if __name__ == '__main__':
    timer = Timer()
    parser = argparse.ArgumentParser(
        description='Show the earliest commit time of a Git repository.')
    parser.add_argument('-r', '--repo', required=True,
                        help='The path to the Git repository.')
    args = parser.parse_args()
    
    if args.repo:
        show_earliest_commit_time(args.repo)

    timer.end()
    timer.show_time_cost()