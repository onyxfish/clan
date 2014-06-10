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
    return '{:,d}'.format(d)

def format_duration(secs):
    """
    Format a duration in seconds as minutes and seconds.
    """
    secs = int(secs)

    if secs > 60:
        mins = secs / 60
        secs = secs - (mins * 60)

        return '%im %02is' % (mins, secs)

    return '%is' % secs

def format_percent(d, t):
    """
    Format a value as a percent of a total.
    """
    return '{:.1%}'.format(float(d) / t)

