import argparse
import sys
import humps

from jekpoint.config import Config


def main(*args, exe_name):
    parser = argparse.ArgumentParser(description='JekPoint CLI')
    parser.add_argument('command', type=str, help='The command to run.')

    if len(args) == 0:
        parser.print_help()
        exit()

    command = humps.decamelize(args[0])

    command_file = getattr(__import__('jekpoint.commands', fromlist=[command]), command)
    if hasattr(command_file, 'add_arguments'):
        command_file.add_arguments(parser)

    args = parser.parse_args()

    config = Config()
    command_file.run(args, config)


if __name__ == '__main__':
    main(*sys.argv[1:], exe_name=sys.argv[0])
