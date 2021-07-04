#!/usr/bin/env python

import sys
import os.path

import ROOT

assert(len(sys.argv) == 3)
fn = sys.argv[1]
fno = sys.argv[2]
assert(os.path.abspath(fn) != os.path.abspath(fno))

assert(os.path.isfile(fn))
f = ROOT.TFile.Open(fn, 'read')
ks = [ k.GetName() for k in f.GetListOfKeys() ]
assert(len(ks) == 1)
dn = ks[0]
d = f.Get(dn)
hs = {}
for k in d.GetListOfKeys():
  n = k.GetName()
  h = d.Get(n)
  h.SetDirectory(0)
  hs[n] = h
f.Close()

fo = ROOT.TFile.Open(fno, 'recreate')
do = fo.mkdir(dn)
do.cd()
for n in sorted(hs.keys()):
  hs[n].Write()
fo.Close()

print("Reordered histograms in {} and saved the result to {}".format(fn, fno))
