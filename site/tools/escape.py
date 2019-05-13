#!/usr/bin/env python3

"""HTML-escape and linkify"""

import fileinput
import html
import re

revision_numbers = re.compile(r'r(\d+)')
issue_references = re.compile(r'((?:SVN-|issue [#]?)(\d+))')

for line in fileinput.input():
    line = html.escape(line)
    line = revision_numbers.sub(r'<a href="https://svn.apache.org/r\1">r\1</a>', line)
    line = issue_references.sub(r'<a href="/issue-\2">\1</a>', line)
    print(line, end='')
