#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script generates a random sequence of two predefined strings."""


import argparse
import random

DEFAULT_LINES = ('la', '')
DEFAULT_AMOUNT = 20


def main():
    """This function parses arguments and executes the main
    logic when script is run as program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--amount', type=int, default=DEFAULT_AMOUNT)
    parser.add_argument('-s', '--seed', default=None)
    args = parser.parse_args()
    random.seed(args.seed)
    for _ in xrange(args.amount):
        print random.choice(DEFAULT_LINES)


if __name__ == '__main__':
    main()
