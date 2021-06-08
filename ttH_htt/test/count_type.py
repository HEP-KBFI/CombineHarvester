#!/usr/bin/env python
import os, subprocess, sys
workingDir = os.getcwd()
import os, re, shlex
from ROOT import *
import numpy as np

from subprocess import Popen, PIPE
# ./rebin_datacards.py --channel "4l_0tau"  --BINtype "regular" --doLimits
from io import open

import glob


hadd_total = glob.glob("/hdfs/local/acaan/hhAnalysis/2016/hh_bb1l_24Jun_SM_default_AK8_LS_fluxogramLike/histograms/hh_bb1l/Tight/TTTo2L2Nu/*_central_*root")

types = ["TT"] # "ZZ" "WH_hww", "WH_htt", "WH_hzz", "ZH_hww", "WH_htt", "WH_hzz",] #"TTW", "TTWW", "TTZ", "WZ", "ZZ", "Rares", "DY", "TT",  "ttZ", "ttH", "tHq", "tHW", "VH", "HH", "ggH", "qqH", "TTWH", "TTZH",] #

sum_all = 0
for type in types :
  sum_by_proc = 0
  for proc in hadd_total :
    try :
        tfile = TFile(proc, "READ")
    except :
        print ("Corrupted: " + proc)
    histCentral = TH1F()
    try :
        histCentral = tfile.Get("hh_bb1l_Tight/sel/evt/%s/HT" % type)
    except :
        continue
    if "hadd" in proc.split("/")[10] :
        print(proc)
        continue
    try :
        integral = histCentral.Integral()
    except :
        continue
    nevents = histCentral.GetEntries()
    print (proc.split("/")[10], type, integral, nevents)
    #print(proc)
    sum_all += integral
    sum_by_proc  += integral
  #print (type, sum_by_proc)
print (sum_all)
