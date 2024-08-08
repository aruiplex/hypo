import argparse
from loguru import logger

parser = argparse.ArgumentParser(
    prog="Hypothesis",
    description="CLI to launch all experiments",
    epilog="Enjoy the training",
)
parser.add_argument(
    "method",
    type=str,
)

# There could be unknown args, so use parse_known_args
args, subargs = parser.parse_known_args()

if "." in args.method:
    args.load_module, args.method = args.method.rsplit(".", 1)
else:
    args.load_module = "index"

logger.info(f"\033[34m[Hypo]: {args}. [Experiments args]: {subargs}")
