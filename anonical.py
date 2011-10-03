#!/usr/bin/env python

import sys, re

pattern = '^BEGIN:VEVENT|^END:VEVENT|^DTSTART|^DTEND|^DURATION|^RRULE'.encode()
match = re.compile(pattern)

if __name__ == '__main__':

    if len(sys.argv) <= 2:
        sys.stderr.write("Run with\n    anonical <inputfile> <outputfile>\n")

    if len(sys.argv) <= 1 or sys.argv[1] == '-':
        infile = sys.stdin
        sys.stderr.write("Using STDIN as input\n")
    else:
        infile = open(sys.argv[1], 'rb')

    if len(sys.argv) <= 2  or sys.argv[2] == '-':
        outfile = sys.stdout
        sys.stderr.write("Using STDOUT as output\n")
    else:
        outfile = open(sys.argv[2], 'wb')

    for line in infile.readlines():
        line = line.upper()
        if match.match(line):
            outfile.write(line)

    sys.stderr.write("Done!\n")