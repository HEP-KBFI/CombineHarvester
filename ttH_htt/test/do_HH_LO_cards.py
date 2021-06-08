#!/usr/bin/env python
import os, subprocess, sys
workingDir = os.getcwd()
import os, re, shlex
from ROOT import *
import numpy as np
import array as arr
from math import sqrt, sin, cos, tan, exp
import glob
import ROOT

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
from io import open

from CombineHarvester.ttH_htt.data_manager_rebin_datacards import testPrint, runCombineCmd, rebinRegular
testPrint()

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--channel ", type="string", dest="channel", help="The ones whose variables implemented now are:\n   - 1l_2tau\n   - 2lss_1tau\n It will create a local folder and store the report*/xml", default="2lss_1tau")
parser.add_option("--output_path", type="string", dest="output_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--prepareDatacards_path", type="string", dest="prepareDatacard_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--flavourCats", action="store_true", dest="flavourCats", help="If you call this will not do plots with repport", default=False)
parser.add_option("--scan_in",      type="string",       dest="scan_in", help="Options: \"kl_scan\" | \"c2_scan\" |  \"shape_BM\" | \"resonance\" ", default="all")
parser.add_option("--HHtype",      type="string",       dest="HHtype", help="Options: \"bbWW\" | \"multilep\" ", default="bbWW")
parser.add_option("--era", type="int", dest="era", help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.", default=2016)
(options, args) = parser.parse_args()

channel    = options.channel
scan_in       = options.scan_in
HHtype       = options.HHtype
era          = options.era
local        = options.output_path
mom          = options.prepareDatacard_path
flavourCats  = options.flavourCats

if scan_in == "kl_scan" :
    signal_type  = "nonresLO"
    BDTfor = "SM"
    masses = [
        "kl_m20p00",
        "kl_m18p00",
        "kl_m16p00",
        "kl_m14p00",
        "kl_m12p00",
        "kl_m10p00",
        "kl_m8p00",
        "kl_m6p00",
        "kl_m4p00",
        "kl_m2p00",
        "kl_0p00",
        "kl_1p00",
        "kl_2p00",
        "kl_2p45",
        "kl_4p00",
        "kl_6p00",
        "kl_8p00",
        "kl_10p00",
        "kl_12p00",
        "kl_14p00",
        "kl_16p00",
        "kl_18p00",
        "kl_20p00",
    ]

elif scan_in == "shape_BM" :
    signal_type  = "nonresLO"
    BDTfor = "SM"
    masses = [
        "SM",
        "BM1",
        "BM2",
        "BM3",
        "BM4",
        "BM5",
        "BM6",
        "BM7",
        "BM8",
        "BM9",
        "BM10",
        "BM11",
        "BM12",
    ]
elif scan_in == "resonance" :
    signal_type  = "res"
    BDTfor = "X900GeV"
    ## not all 3 final states have all masses
    masses = [
        #"spin0_250",
        "spin0_260",
        ##"spin0_270",
        #"spin0_280",
        ##"spin0_300",
        #"spin0_320",
        #"spin0_340",
        "spin0_350",
        "spin0_400",
        "spin0_450",
        "spin0_500",
        ##"spin0_550",
        "spin0_600",
        #"spin0_650",
        "spin0_800",
        "spin0_900",
    ]

if channel == "1l_0tau" :
    ch_nickname = "hh_bb1l_hh_bb1l"
    # name card : nbins
    categories = {
        "cat_jet_2BDT_Wjj_simple_%s_HbbFat_WjjRes_allReco" % BDTfor : 50,
        "cat_jet_2BDT_Wjj_simple_%s_Res_allReco"           % BDTfor : 75
    }
    if flavourCats :
        categories = {
            "cat_jet_2BDT_Wjj_simple_%s_HbbFat_WjjRes_allReco_e" % BDTfor : 35,
            "cat_jet_2BDT_Wjj_simple_%s_HbbFat_WjjRes_allReco_m" % BDTfor : 50,
            "cat_jet_2BDT_Wjj_simple_%s_Res_allReco_1b_e"        % BDTfor : 60,
            "cat_jet_2BDT_Wjj_simple_%s_Res_allReco_1b_m"        % BDTfor : 75,
            "cat_jet_2BDT_Wjj_simple_%s_Res_allReco_2b_e"        % BDTfor : 30,
            "cat_jet_2BDT_Wjj_simple_%s_Res_allReco_2b_m"        % BDTfor : 40,
        }
elif channel == "2l_0tau" :
    ch_nickname = "hh_bb2l_hh_bb2l_OS"
    categories = {
    "SM_plainVars_inclusive"           : 45
    }
else :
    print ("Channel %s not implemented" % channel)
    sys.exit()

import shutil,subprocess
proc=subprocess.Popen(["mkdir %s" % local],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()
mom_datacards = "%s/datacards_rebined/" % local
proc=subprocess.Popen(["mkdir %s" % mom_datacards],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()

nameOutFileAdd = "_multisig"

nameOutFileAdd = nameOutFileAdd + "_" + str(era)

### first we do one datacard.txt / bdtType
sources           = []
bdtTypesToDo      = []
bdtTypesToDoLabel = []
sourcesCards      = []
sourcesCardsLabel = []
counter=0
for ii, bdtType in enumerate(list(categories.keys())) :
    fileName = mom   + "/prepareDatacards_" + ch_nickname + "_" + bdtType + ".root"
    source   = local + "/prepareDatacards_" + ch_nickname + "_" + bdtType
    print (fileName)
    if os.path.isfile(fileName) :
        proc              = subprocess.Popen(['cp ' + fileName + " " + local],shell=True,stdout=subprocess.PIPE)
        out = proc.stdout.read()
        sources           = sources + [source]
        bdtTypesToDo      = bdtTypesToDo +[channel+" "+bdtType]
        bdtTypesToDoLabel = bdtTypesToDoLabel + [channel+" "+bdtType]
        ++counter
        print ("rebinning ", sources[counter])
    else : print ("does not exist ",source)
print ("I will rebin", bdtTypesToDoLabel,"(",len(sources),") BDT options")

for nn, source in enumerate(sources) :
  for mass in masses :
    outfile = "%s" % (source.replace("prepareDatacards_", "datacard_"))

    cmd = "WriteDatacards.py "
    cmd += "--inputShapes %s.root " % (source)
    cmd += "--channel %s " % channel
    cmd += "--output_file %s " % (outfile)
    cmd += "--noX_prefix --era %s  --no_data --analysis HH " % str(era)

    cmd += " --signal_type %s "      % signal_type
    cmd += " --mass %s "             % mass
    cmd += " --HHtype bbWW"
    log_datacard = "%s_datacard.log" % source
    runCombineCmd(cmd, ".", log_datacard)

    didCard = False
    for line in open(log_datacard):
        if "Output file:" in line :
            fileCard = line.split(" ")[3].replace("'","").replace(",","").replace(".txt","") #splitPath(lineL)[1]
            print("done card %s.txt" % fileCard)
            didCard = True
            break
    if didCard == False :
        print ("!!!!!!!!!!!!!!!!!!!!!!!! The WriteDatacards did not worked, to debug please check %s to see up to when the script worked AND run again for chasing the error:" % log_datacard)
        print(cmd)
        sys.exit()
    sourcesCards = sourcesCards + [ fileCard ]
    sourcesCardsLabel = sourcesCardsLabel + [bdtTypesToDo[nn]]

#for nn, sourceL in enumerate(list(categories.keys()))  :
for nn, sourceL in enumerate(sourcesCards)  :
        print ( "rebining %s" % sourcesCards[nn] )
        numberBins = 0
        iscat = "test"
        for nnn, ncat  in enumerate(list(categories.keys())) :
            if ncat in sourceL :
                numberBins = categories[ncat]
                iscat = ncat
        errOcont = rebinRegular(
            sourcesCards[nn],
            [numberBins],
            "regular",
            100,
            False,
            sourcesCardsLabel[nn],
            mom_datacards,
            nameOutFileAdd,
            True
            )
        ## copy the txt
        fileCardOnlyL = sourcesCards[nn].split("/")[len(sourcesCards[nn].split("/")) -1]
        fileCardOnlynBinL = "%s_%s%s" % (fileCardOnlyL, str(categories[iscat]), nameOutFileAdd)
        fileCardL = "%s/%s" % (mom_datacards, fileCardOnlynBinL)
        print ("make limit for %s.txt" % fileCardL)
        runCombineCmd("cp %s.txt %s.txt" % (sourcesCards[nn], fileCardL))
        with open("%s.txt" % fileCardL,'r+') as ff:
            filedata = ff.read()
            filedata = filedata.replace(fileCardOnlyL, fileCardOnlynBinL)
            ff.truncate(0)
            ff.write(filedata)


"""
cd prepareDatacards_path
hadd prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_MissJet.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_MissJet_e.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_MissJet_m.root
hadd prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_allReco.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_allReco_e.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_allReco_m.root
hadd prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_MissWJet.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_MissWJet_1b_e.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_MissWJet_1b_m.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_MissWJet_2b_e.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_MissWJet_2b_m.root
hadd prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_allReco.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_allReco_1b_e.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_allReco_1b_m.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_allReco_2b_e.root prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_SM_Res_allReco_2b_m.root
"""
