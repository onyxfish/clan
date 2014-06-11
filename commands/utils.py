#!/usr/bin/env python

GLOBAL_ARGUMENTS = [
    'property-id',
    'start-date',
    'end-date',
    'ndays',
    'domain',
    'prefix',
] 

def format_comma(d):
    """
    Format a comma separated number.
    """
    return '{:,}'.format(d)

def format_duration(secs):
    """
    Format a duration in seconds as minutes and seconds.
    """
    secs = int(secs)

    if abs(secs) > 60:
        mins = abs(secs) / 60
        secs = abs(secs) - (mins * 60)

        return '%s%im %02is' % ('-' if secs < 0 else '', mins, secs)

    return '%is' % secs

def format_percent(d, t):
    """
    Format a value as a percent of a total.
    """
    return '{:.1%}'.format(float(d) / t)

