#!/usr/bin/env python

import ROOT
import sys
import os.path

MODES = [ 'exclude_higgs', 'extract_stxs' ]
PROCS = [ 'ttH', 'ggH', 'qqH', 'WH', 'ZH' ]

assert(len(sys.argv) == 4)
fn_in = sys.argv[1]
fn_out = sys.argv[2]
mode = sys.argv[3]

assert(os.path.abspath(fn_in) != os.path.abspath(fn_out))

assert(os.path.isfile(fn_in))
assert(fn_in.endswith('.root'))
assert(fn_out.endswith('.root'))
assert(mode in MODES)
exclude_higgs = mode == 'exclude_higgs'

fptr_in = ROOT.TFile.Open(fn_in, 'read')
fptr_keys = [ key.GetName() for key in fptr_in.GetListOfKeys() ]
assert(len(fptr_keys) == 1)
dirn = fptr_keys[0]
assert(dirn)
dirptr = fptr_in.Get(dirn)

hkeys = [ key.GetName() for key in dirptr.GetListOfKeys() ]
hkeys_sel = [ hkey for hkey in hkeys if exclude_higgs != hkey.startswith(tuple(PROCS)) ]
hists = []
for hkey in hkeys_sel:
  hist = dirptr.Get(hkey)
  hist.SetDirectory(0)
  hists.append(hist)
fptr_in.Close()

fptr_out = ROOT.TFile.Open(fn_out, 'recreate')
dirptr_out = fptr_out.mkdir(dirn)
dirptr_out.cd()
for hist in hists:
  hist.Write()
fptr_out.Close()
