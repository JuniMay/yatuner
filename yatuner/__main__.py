# -*- coding: utf-8 -*-

# Copyright (c) 2022 Synodic Month, Juni May
# yaTuner is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import yatuner
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(prog='yatuner',
                                     description=yatuner.__doc__)
    parser.add_argument('-g',
                        '--generate',
                        type=str,
                        dest='filename',
                        help="Automatic generate basic tuning script")

    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.filename is not None:
        yatuner.generate(args.filename)


if __name__ == '__main__':
    main()