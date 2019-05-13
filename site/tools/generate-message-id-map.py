#!/usr/bin/env python
# Regenerate 'publish/.message-ids.tsv'
#
# - Search files under 'publish/' for URLs of messages in the haxx.se
#   archives. Compile a list of <URL><TAB><MESSAGE-ID>.
# - Commit the result if it has changed.
#
# Run this in a Subversion 'site' working copy.
#

import subprocess

fn = "publish/.message-ids.tsv"

old_lines = open(fn).readlines()
new_lines = subprocess.check_output(['tools/haxx-url-to-message-id.sh', 'publish']).splitlines(True)
old_lines_cmp = [l for l in old_lines if not l.startswith('#')]
new_lines_cmp = [l for l in new_lines if not l.startswith('#')]
if old_lines_cmp != new_lines_cmp:
  with open(fn, 'w') as f:
    f.writelines(new_lines)
  subprocess.check_call(['svn', 'ci', '-q',
                         '-m', '* ' + fn + ': Automatically regenerated.',
                         fn])
