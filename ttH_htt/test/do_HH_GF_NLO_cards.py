#!/usr/bin/env python
import os, subprocess, sys
workingDir = os.getcwd()
import os, re, shlex
from ROOT import *
import numpy as np
import array as arr
from math import sqrt, sin, cos, tan, exp
import glob

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
# ./rebin_datacards.py --channel "4l_0tau"  --BINtype "regular" --doLimits
from io import open

functions = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager_rebin_datacards.py"
class mainprogram():
    def runme(self):
        execfile(functions)
this = mainprogram()
this.runme()
testPrint()

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--channel ", type="string", dest="channel", help="The ones whose variables implemented now are:\n   - 1l_2tau\n   - 2lss_1tau\n It will create a local folder and store the report*/xml", default="2lss_1tau")
parser.add_option("--output_path", type="string", dest="output_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--prepareDatacards_path", type="string", dest="prepareDatacard_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--flavourCats", action="store_true", dest="flavourCats", help="If you call this will not do plots with repport", default=False)
parser.add_option("--signal",      type="string",       dest="signal", help="Options: \"DL\" | \"SL\" | \"bbtt\"  | \"all\" ", default="all")
parser.add_option("--HHtype",      type="string",       dest="HHtype", help="Options: \"bbWW\" | \"multilep\" ", default="bbWW")
parser.add_option("--era", type="int", dest="era", help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.", default=2016)
(options, args) = parser.parse_args()

channel    = options.channel
signal       = options.signal
HHtype       = options.HHtype
era          = options.era
local        = options.output_path
mom          = options.prepareDatacard_path
flavourCats  = options.flavourCats
signal_type  = "nonresNLO"

if channel == "1l_0tau" :
    ch_nickname = "hh_bb1l_hh_bb1l"
    # name card : nbins
    categories = {
        "cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_allReco" : 50,
        "cat_jet_2BDT_Wjj_simple_SM_Res_allReco"           : 75
    }
    if flavourCats :
        categories = {
            "cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_allReco_e" : 35,
            "cat_jet_2BDT_Wjj_simple_SM_HbbFat_WjjRes_allReco_m" : 50,
            "cat_jet_2BDT_Wjj_simple_SM_Res_allReco_1b_e"        : 60,
            "cat_jet_2BDT_Wjj_simple_SM_Res_allReco_1b_m"        : 75,
            "cat_jet_2BDT_Wjj_simple_SM_Res_allReco_2b_e"        : 30,
            "cat_jet_2BDT_Wjj_simple_SM_Res_allReco_2b_m"        : 40,
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

if signal == "DL" :
    # coonsider only DL
    nameOutFileAdd = "_onlyDL"
elif signal == "SL" :
    # coonsider only DL
    nameOutFileAdd = "_onlySL"
elif signal == "bbtt" :
    # coonsider only DL
    nameOutFileAdd = "_onlyBBTT"
else :
    # coonsider all possible ggHH
    nameOutFileAdd = "_multisig"
nameOutFileAdd = nameOutFileAdd + "_" + str(era)

### first we do one datacard.txt / bdtType
sources           = []
bdtTypesToDo      = []
bdtTypesToDoLabel = []
sourcesCards      = []
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
    outfile = "%s" % (source.replace("prepareDatacards_", "datacard_"))

    cmd = "WriteDatacards.py "
    cmd += "--inputShapes %s.root " % (source)
    cmd += "--channel %s " % channel
    cmd += "--output_file %s " % (outfile)
    cmd += "--noX_prefix --era %s  --no_data --analysis HH " % str(era)
    cmd += " --renamedHHInput "
    ## TODO add only_HH_sig in WriteDatacards

    cmd += " --signal_type %s "      % signal_type
    #cmd += " --mass %s "             % mass
    if signal == "DL" :
        # coonsider only DL
        cmd += " --HHtype bbWW_DL "
    elif signal == "SL" :
        # coonsider only DL
        cmd += " --HHtype bbWW_SL "
    elif signal == "bbtt" :
        # coonsider only bbtt
        cmd += " --HHtype bbWW_bbtt "
    else :
        # coonsider all possible ggHH
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

if 1 > 0 :
    for nn, sourceL in enumerate(list(categories.keys()))  :
        print ( "rebining %s" % sourcesCards[nn] )
        errOcont = rebinRegular(
            sourcesCards[nn],
            [categories[sourceL]],
            "regular",
            100,
            False,
            bdtTypesToDo[nn],
            mom_datacards,
            nameOutFileAdd,
            True
            )
        ## copy the txt
        fileCardOnlyL = sourcesCards[nn].split("/")[len(sourcesCards[nn].split("/")) -1]
        fileCardOnlynBinL = "%s_%s%s" % (fileCardOnlyL, str(categories[sourceL]), nameOutFileAdd)
        fileCardL = "%s/%s" % (mom_datacards, fileCardOnlynBinL)
        print ("make limit for %s.txt" % fileCardL)
        runCombineCmd("cp %s.txt %s.txt" % (sourcesCards[nn], fileCardL))
        with open("%s.txt" % fileCardL,'r+') as ff:
            filedata = ff.read()
            filedata = filedata.replace(fileCardOnlyL, fileCardOnlynBinL)
            ff.truncate(0)
            ff.write(filedata)
