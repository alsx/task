#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains tests of triggered_sequester module."""

import unittest

from apps.triggered_sequester import triggered_sequester


class TestTriggeredSequester(unittest.TestCase):

    """Contains test cases to verify triggered_sequester function."""

    def test_empty(self):
        """Checks whether pass list with one empty line."""
        sample = ['']
        result = list(triggered_sequester(sample))
        self.assertListEqual(result, [])

    def test_lead_empty(self):
        """Checks whether remove lead empty line."""
        sample = ['', 'la']
        result = list(triggered_sequester(sample))
        self.assertListEqual(result, ['la'])

    def test_final_empty(self):
        """Checks whether remove final empty line."""
        sample = ['la', '']
        result = list(triggered_sequester(sample))
        self.assertListEqual(result, ['la'])

    def test_several_empty(self):
        """Checks whether unites empty lines into the one is working correct."""
        sample = ['', '', 'la', '', '', '', 'la', '', '']
        result = list(triggered_sequester(sample))
        self.assertListEqual(result, ['la', '', 'la'])

    def test_not_iterable(self):
        """Checks whether raised appropriate error for non-iterable argument."""
        sample = 0
        with self.assertRaises(TypeError):
            _ = list(triggered_sequester(sample))

    def test_g18n(self):
        """Checks non-unicode strings are handled correctly."""
        sample = ['', '汉语/漢語', 'カタカナ', 'кирилиця', 'العربية', '']
        result = list(triggered_sequester(sample))
        self.assertListEqual(result, sample[1:-1])

    def test_trim_newlines(self):
        sample = ['\n\nla\n\n', '\n']
        result = list(triggered_sequester(sample, trim=lambda x: x.strip('\n')))
        self.assertListEqual(result, ['la'])


if __name__ == '__main__':
    unittest.main()
