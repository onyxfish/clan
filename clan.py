#!/usr/bin/env python

import argparse
import sys 

from oauth2client import tools

from commands import AuthCommand, DiffCommand, ReportCommand

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

        subparsers = self.argparser.add_subparsers()

        # Authentication
        parser_auth = subparsers.add_parser('auth', parents=[generic_parser, tools.argparser])
        parser_auth.set_defaults(func=AuthCommand())

        parser_auth.add_argument(
            '--secrets',
            dest='secrets', action='store',
            help='Path to the authorization secrets file (client_secrets.json).'
        )

        # Reporting
        parser_report = subparsers.add_parser('report', parents=[generic_parser])
        parser_report.set_defaults(func=ReportCommand())

        parser_report.add_argument(
            '--auth',
            dest='auth', action='store',
            help='Path to the authorized credentials file (analytics.dat).'
        )

        parser_report.add_argument(
            '-c', '--config',
            dest='config_path', action='store', default='clan.yml',
            help='Path to a YAML configuration file (clan.yml).'
        )

        parser_report.add_argument(
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing JSON report file.'
        )

        parser_report.add_argument(
            '-f', '--format',
            dest='format', action='store', default='txt', choices=['txt', 'json'],
            help='Output format.'
        )

        parser_report.add_argument(
            '--property-id',
            dest='property-id', action='store',
            help='Google Analytics ID of the property to query.'
        )

        parser_report.add_argument(
            '--start-date',
            dest='start-date', action='store',
            help='Start date for the query in YYYY-MM-DD format.'
        )

        parser_report.add_argument(
            '--end-date',
            dest='end-date', action='store',
            help='End date for the query in YYYY-MM-DD format. Supersedes --ndays.'
        )

        parser_report.add_argument(
            '--ndays',
            dest='ndays', action='store', type=int,
            help='The number of days from the start-date to query. Requires start-date. Superseded by end-date.'
        )

        parser_report.add_argument(
            '--domain',
            dest='domain', action='store',
            help='Restrict results to only urls with this domain.'
        )

        parser_report.add_argument(
            '--prefix',
            dest='prefix', action='store',
            help='Restrict results to only urls with this prefix.'
        )

        parser_report.add_argument(
            'output',
            action='store',
            help='Output file path.'
        )
        
        # Diff
        parser_report = subparsers.add_parser('diff', parents=[generic_parser])
        parser_report.set_defaults(func=DiffCommand())

        parser_report.add_argument(
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing JSON diff file.'
        )

        parser_report.add_argument(
            '-f', '--format',
            dest='format', action='store', default='txt', choices=['txt', 'json'],
            help='Output format.'
        )

        parser_report.add_argument(
           'report_a',
            action='store',
            help='First JSON report file path.'
        )

        parser_report.add_argument(
           'report_b',
            action='store',
            help='Second JSON report file path.'
        )

        parser_report.add_argument(
            'output',
            action='store',
            help='Output file path.'
        )

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

