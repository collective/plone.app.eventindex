#!/usr/bin/env python

import sys, re

match = re.compile('^BEGIN:VEVENT|^END:VEVENT|^DTSTART;|^DTEND;|^DURATION;|^RRULE;')

if __name__ == '__main__':

    if len(sys.argv) <= 2:
        sys.stderr.write("Run with\n    anonical <inputfile> <outputfile>\n")

    if len(sys.argv) <= 1 or sys.argv[1] == '-':
        infile = sys.stdin
        sys.stderr.write("Using STDIN as input\n")
    else:
        infile = open(sys.argv[1], 'rt')

    if len(sys.argv) <= 2  or sys.argv[2] == '-':
        outfile = sys.stdout
        sys.stderr.write("Using STDOUT as output\n")
    else:
        outfile = open(sys.argv[2], 'wt')

    for line in infile.xreadlines():
        line = line.upper()
        if match.match(line):
            outfile.write(line)

    sys.stderr.write("Done!\n")