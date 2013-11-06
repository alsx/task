#!/usr/bin/env python
"""This module contains classes to work with log files."""
import argparse
import itertools
import re
import time

from datetime import datetime, timedelta

__all__ = ['Line', 'Resource', 'Broker']

DATETIME_FORMAT = '%a %b %d %Y %H:%M:%S'
LEVELS = ('debug', 'info', 'warning', 'error', 'critical')
PATTERN = re.compile('\\[(?P<timestamp>[\\sA-Za-z0-9\\:]+) (?P<tz_sign>\\+|-)'
                     '(?P<tz_hours>\\d{2})(?P<tz_mins>\\d{2})\\] '
                     '\\[(?P<level>[a-z]+)\\]')


class Line(object):

    """This class reflect line of log as object and provide
    mechanism to compare and converting back to string.
    """

    timestamp = None
    level = None
    line = None

    def __init__(self, str_):
        if str_:
            self.line = str_
            matched = PATTERN.search(self.line)
            self.level = matched.group('level')
            self.timestamp = self.utc_timestamp(matched.group('timestamp'),
                                                matched.group('tz_sign'),
                                                matched.group('tz_hours'),
                                                matched.group('tz_mins'))

    def __cmp__(self, other):
        return cmp(self.timestamp, other.timestamp)

    def __str__(self):
        return self.line

    def __nonzero__(self):
        return bool(self.line)

    @staticmethod
    def utc_timestamp(time_string, tz_sign, tz_hours, tz_mins):
        """Looks tricky, but I do not see reason to reinvent the wheel
        when python's stdlib do not include tools to parse time sting
        with time zones.

        :Parameters:
            -`time_string`: datetime as formatted string.
            -`tz_sign`: sign of time zone.
            -`tz_hours`: hours time shifted.?
            -`tz_mins`: minutes time shifted.?

        :Return:
            - Integer time.
        """
        raw_dt = datetime.strptime(time_string, DATETIME_FORMAT)
        delta = timedelta(hours=int(tz_hours), minutes=int(tz_mins))
        if tz_sign == '+':
            utc_dt = raw_dt + delta
        else:
            utc_dt = raw_dt - delta
        return int(time.mktime(utc_dt.timetuple()))


class Resource(object):

    """Class accepts file and passes through its lines as iterator."""

    def __init__(self, file_):
        if type(file_) is file:
            self.file_ = file_
        else:
            self.file_ = open(file_)

        # default lines parser
        self._line = Line

    @property
    def line(self):
        """Weak composition with object of line."""
        return self._line

    @line.setter
    def line(self, line_parser):
        """Redefines object of line.

        :Parameters:
            -`line_parser`: class to parse lines of log.
        """
        self._line = line_parser

    def __iter__(self):
        return self

    def next(self):
        """Iterate lines of file."""
        line = self._line(self.file_.readline())
        while True:
            if line:
                return line
            else:
                self.file_.close()
            raise StopIteration


class Broker(object):

    """This class handles a bunch of files and composes them into one."""

    def __init__(self):
        self.resoures = []
        self.max_level_index = LEVELS[-1]
        self.files = []
        self._most_priority = min
        self._front_line = []

    def add_files(self, files):
        """Add list of files.

        :Parameters:
            -`files`: list file objects or file paths.

        :Return:
            - `self` for chaining.
        """
        self.files += files
        return self

    def filter_(self, iterator):
        """Filter line by level.

        :Parameters:
            -`iterator`: line iterator.

        :Return:
            - iterator with filter.
        """
        def is_important(line):
            """Condition of passing filter."""
            return LEVELS.index(line.level) >= self.max_level_index

        return itertools.ifilter(is_important, iterator)

    def sort(self, order=None):
        """Set a function to get the most priority value from front line list.

        :Parameters:
            - `order`: function. Ex.: lambda x: x[0]
        :Return:
            `self` for chaining.
        """
        if order is not None:
            self._most_priority = order
        return self

    def where(self, max_level):
        """Set which level of messages have meaning.

        :Parameters:
            - `max_level`: message level. Could be: 'debug', 'info', 'warning',
            'error' or 'critical'
        :Return:
            `self` for chaining.
        """

        self.max_level_index = LEVELS.index(max_level.lower())
        return self

    def _preload(self):
        """This method opens log files and loads the first line
        of each file into list."""
        for file_ in self.files:
            self.resoures.append(Resource(file_))

        for item in self.resoures:
            next_ = self.filter_(item).next()
            self._front_line.append(next_)

    def _fanin(self):
        """This method realise Fan-in message broker pattern.

        -- queues --->      v---- front line
        12 10  8  6  4    | 2|
        11  9  7  5 {3}-> |  | {1} -> pop the most priority value
        22 20 18 17 16 |  |15|
                       +-------- substitute by new value from queue
                                 into empty cell of front line list

        :Return:
            - iterator of ordered and filtered lines
        """

        while True:
            # define the most priority line between current lines of each logs
            sooner = self._most_priority(self._front_line)
            # get index of file in list to substitute popped value
            sooner_index = self._front_line.index(sooner)
            to_output = self._front_line[sooner_index]
            # substitute by new value from queue
            next_ = self.filter_(self.resoures[sooner_index]).next()
            if next_ is None:
                # on EOF remove closed file from resources and front line list
                del self.resoures[sooner_index]
                del self._front_line[sooner_index]
            else:
                self._front_line[sooner_index] = next_

            yield to_output

    def run(self):
        """Start parsing logs."""
        self._preload()
        return self._fanin()


def main():
    """Parse command line arguments.
    Combine several log files into one (chronologically and filtered by level).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--level', default=LEVELS[0], choices=LEVELS,
                        help='Level of messages.')
    parser.add_argument('infile', type=argparse.FileType('r'), nargs='+',
                        help='List of log files.')
    args = parser.parse_args()
    level = args.level
    files = args.infile
    rows = Broker().add_files(files).where(max_level=level).run()
    for row in rows:
        print row,


if __name__ == '__main__':
    main()
