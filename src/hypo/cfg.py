import argparse
from loguru import logger

parser = argparse.ArgumentParser(
    prog="Hypothesis",
    description="CLI to launch all experiments",
    epilog="Enjoy the training",
)
parser.add_argument(
    "expName",
    type=str,
    nargs='?',
    default="",
    help="Experiment name",
)
parser.add_argument(
    "method",
    type=str,
)

# There could be unknown args, so use parse_known_args
args, subargs = parser.parse_known_args()

if args.expName != "":
    args.expName = args.expName + "."

logger.info(f"\033[34m[Hypo]: {args}")
logger.info(f"\033[34m[Experiments args]: {subargs}")
