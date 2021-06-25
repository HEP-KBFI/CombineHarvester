#!/usr/bin/env python

import sys
import os.path
import re

assert(len(sys.argv) == 2)
fn_txt = sys.argv[1]
assert(os.path.isfile(fn_txt))
assert(fn_txt.endswith('.txt'))

fn_root = re.sub('.txt$', '.root', fn_txt)
assert(os.path.isfile(fn_root))
fn_root_base = os.path.basename(fn_root)

changed = False
lines = []
with open(fn_txt, 'r') as fptr_txt:
  for line in fptr_txt:
    ls = line.rstrip('\n')
    if ls.startswith('shapes'):
      ls_split = ls.split()
      ls_root = ls_split[3]
      if ls_root != fn_root_base:
        ls_new = ls.replace(' {} '.format(ls_root), ' {} '.format(fn_root_base))
        lines.append(ls_new)
        changed = True
      else:
        lines.append(ls)
    else:
      lines.append(ls)
lines.append('')

if changed:
  print("Changed {} to {} in {}".format(ls_root, fn_root_base, fn_txt))
  with open(fn_txt, 'w') as fptr_txt:
    fptr_txt.write('\n'.join(lines))
