#!/usr/bin/env python

import ROOT
import sys
import os.path

assert(len(sys.argv) == 3)
ifn = sys.argv[1]
ofn = os.path.abspath(sys.argv[2])
assert(os.path.isfile(ifn))
assert(os.path.isdir(os.path.dirname(ofn)))

ifptr = ROOT.TFile.Open(ifn, 'read')
ikeys = [ k.GetName() for k in ifptr.GetListOfKeys() ]
hists = []
for k in ikeys:
  if k.startswith('ttH'):
    continue
  hist = ifptr.Get(k)
  hist.SetDirectory(0)
  hists.append(hist)
ifptr.Close()

ofptr = ROOT.TFile.Open(ofn, 'recreate')
ofptr.cd()
for hist in hists:
  hist.Write()
ofptr.Close()

print(
  'Excluded {} histograms out of {} in {}'.format(
    len(ikeys) - len(hists),
    len(ikeys),
    ofn,
  )
)
