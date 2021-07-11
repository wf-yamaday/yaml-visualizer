import argparse
import logging
import sys
import datetime
import graphviz

from ..compose.main import dispatch
from .dot import can_use_graphviz

log = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="input filename. default: ./docker-compose.yml")
    parser.add_argument(
        "-o", "--output", help="output filename. default: output-YYYYmmdd-HHMMSS.png")

    args = parser.parse_args()

    if not can_use_graphviz():
        msg = 'cannot find graphviz. please install graphviz.'
        exit_with_msg(msg)

    input_filename = './docker-compose.yml'
    if args.input != None:
        input_filename = args.input

    dt_now = datetime.datetime.now()
    output_filename = 'output-{}'.format(dt_now.strftime('%Y%m%d-%H%M%S'))
    if args.output != None:
        output_filename = args.output

    try:
        g = dispatch(input_filename)
    except FileNotFoundError as e:
        msg = 'No such file: {}'.format(input_filename)
        exit_with_msg(msg)

    try:
        g.render(filename=output_filename, cleanup=True, view=False)
    except (ValueError, graphviz.RequiredArgumentError, graphviz.ExecutableNotFound, RuntimeError) as e:
        exit_with_msg(e.msg)

    msg = 'Complete! output file: {}.png'.format(output_filename)
    exit_with_msg(msg, exit_code=0)


def exit_with_msg(log_msg=None, exit_code=1):
    if not exit_code:
        log.info(log_msg)
    else:
        log.error(log_msg)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
