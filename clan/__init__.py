#!/usr/bin/env python

import argparse
import sys 

from clan.auth import AuthCommand
from clan.diff import DiffCommand
from clan.report import ReportCommand

COMMANDS = [
    AuthCommand,
    ReportCommand,
    DiffCommand
]

class Clan(object):
    """
    Command-line interface to Google Analytics.
    """
    def __init__(self):
        """
        Setup and parse command line arguments.
        """
        self._install_exception_handler()

        self.argparser = argparse.ArgumentParser(
            description='A command-line interface to Google Analytics'
        )

        # Generic arguments
        generic_parser = argparse.ArgumentParser(add_help=False)

        generic_parser.add_argument(
            '-v', '--verbose',
            dest='verbose', action='store_true',
            help='Print detailed tracebacks when errors occur.'
        )

        # Command parsers
        subparsers = self.argparser.add_subparsers()

        for cls in COMMANDS:
            command = cls()
            command.add_argparser(subparsers, [generic_parser])

        self.args = self.argparser.parse_args()
        self.args.func(self.args)

    def _install_exception_handler(self):
        """
        Installs a replacement for sys.excepthook, which handles pretty-printing uncaught exceptions.
        """
        def handler(t, value, traceback):
            if self.args.verbose:
                sys.__excepthook__(t, value, traceback)
            else:
                sys.stderr.write('%s\n' % unicode(value).encode('utf-8'))

        sys.excepthook = handler

def _main():
    Clan()
    
if __name__ == "__main__":
    _main()