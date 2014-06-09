#!/usr/bin/env python

import argparse
import sys 

import clan.foo

class Clan(object):

    def __init__(self, args=None, output_file=None):
        """
        Setup.
        """
        self.argparser = argparse.ArgumentParser(
            description='TKTK',
            epilog='TKTK'
        )

        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')

        self.args = self.argparser.parse_args(args)

        self._install_exception_handler()

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

    def main(self):
        print clan.foo.bar 
                
def _main():
    clan = Clan()
    clan.main()
    
if __name__ == "__main__":
    _main()

