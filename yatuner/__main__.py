import yatuner
import argparse

parser = argparse.ArgumentParser(prog='yatuner', description=yatuner.__doc__)
parser.add_argument('-g',
                    '--generate',
                    type=str,
                    dest='filename',
                    help="Automatic generate basic tuning script")

args = parser.parse_args()

if args.filename is not None:
    yatuner.generate(args.filename)