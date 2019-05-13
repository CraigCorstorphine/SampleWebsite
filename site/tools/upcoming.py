#! /usr/bin/env python3

"""
WIP - INCOMPLETE

Generate 'svn log' output since the last tag to HEAD of the release branch,
filtering all but merge commits.
"""

import datetime
import os
import re
import subprocess
import sys
import tempfile

import xml.etree.ElementTree as ET

SVN = os.getenv('SVN', 'svn')
LOG_SEPARATOR_LINE = ('-' * 72) + '\n'
DIST_RELEASE_URL = 'https://dist.apache.org/repos/dist/release/subversion'

def copyfrom_revision_of_previous_tag_of_this_stable_branch():
    """Returns the copyfrom revision of the previous tag of the stable branch
    checked out in cwd."""
    ### Doesn't work during the alpha/beta/rc phase; works only after 1.A.0 has been tagged
    version_string = subprocess.check_output(['build/getversion.py', 'SVN', 'subversion/include/svn_version.h']).decode()
    version_broken_down = list(map(int, version_string.split('.')))
    files_list = subprocess.check_output([SVN, 'ls', '--', DIST_RELEASE_URL]).decode().splitlines()
    while version_broken_down[-1] > 0:
        version_broken_down[-1] -= 1
        if any(x.startswith('subversion-' + '.'.join(map(str, version_broken_down)) + '.tar.')
               for x in files_list):
            break
    else:
        assert False, "Couldn't find last release preceding {!r}".format(version_string)
    target = '^/subversion/tags/' + '.'.join(map(str, version_broken_down))
    log_output = \
        subprocess.check_output(
            [SVN, 'log', '-q', '-v', '-l1', '-rHEAD:0', '--stop-on-copy', '--', target]
        ).decode()
    return int(re.compile(r'[(]from \S*:(\d+)[)]').search(log_output).group(1))

def get_merges_for_range(start, end):
    """Return an array of revision numbers in the range -r START:END that are
    merges.  START must be an integer; END need not be."""

    cache = []
    revisions = \
        subprocess.check_output(
            [SVN, 'log', '--xml', '-v', '-r', str(start) + ":" + str(end)],
        ).decode()
    log_xml = ET.fromstring(revisions)

    relative_url = subprocess.check_output([SVN, 'info', '--show-item', 'relative-url']).decode().rstrip('\n')

    for logentry in log_xml.findall('./logentry'):
        is_merge = relative_url[1:] in (path.text for path in logentry.findall('.//path'))
        if is_merge:
            yield logentry

def main():
    start_revision = copyfrom_revision_of_previous_tag_of_this_stable_branch() + 1
    for logentry in get_merges_for_range(start_revision, "HEAD"):
        f = lambda s: logentry.findall('./' + s)[0].text
        f.__doc__ = """Get the contents of the first child tag whose name is given as an argument."""
        print(LOG_SEPARATOR_LINE, end='')
        print("r%(revision)s | %(author)s | %(date)s | %(linecount)s lines" % dict(
            revision  = logentry.attrib['revision'],
            author    = f('author'),
            date      = datetime.datetime.strptime(f('date'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S +0000 (%a, %d %b %Y)'),
            linecount = 1+len(f('msg').splitlines()), # increment because of the empty line printed next
        ))
        print()
        print(f('msg'))

    print(LOG_SEPARATOR_LINE, end='')

if __name__ == '__main__':
    main()
