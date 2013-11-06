#!/usr/bin/env python
"""This module contains a function that filters the sequence
and leaves only one blank line between the nonempty.
"""

__all__ = ['triggered_sequentor']

import argparse
import collections
import sys


def triggered_sequester(sequence, trim=None):
    """This iterator filters the sequence of lines and
    leaves only one blank line between the non empty lines.

    :Parameters:
        -`sequence`: iterable sequence of string.
        -`trim`: lambda function that returns the given string
        without the rudimentary characters.

    :Return:
        - iterator of processed string.

    """
    # set the initial state
    is_prev_not_empty = False
    is_previous_empty = False
    if not isinstance(sequence, collections.Iterable):
        raise TypeError('Given sequence is not iterable')

    for line in sequence:
        if trim is not None:
            line = trim(line)
        if line:
            # If between the previous and current not empty lines were
            # one or several blank lines then returns one empty line.
            if is_previous_empty and is_prev_not_empty:
                is_prev_not_empty = False
                yield ''

            is_prev_not_empty = True
            is_previous_empty = False
            yield line
        else:
            is_previous_empty = True


def main():
    """This function parses arguments and executes the main
    logic when script is run as program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    args = parser.parse_args()
    trim = lambda x: x.strip('\r\n"\'')
    for line in triggered_sequester(args.infile.readlines(), trim=trim):
        print "'%s', " % (line,),


if __name__ == '__main__':
    main()
