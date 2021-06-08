#!/usr/bin/env python
import os, shlex
from subprocess import Popen, PIPE
import glob
import shutil
import ROOT
from collections import OrderedDict

# python test/rename_procs.py --inputPath /home/acaan/hhAnalysis/2016/hh_bb1l_23Jul_baseline_TTSL/datacards/hh_bb1l/prepareDatacards/ --card prepareDatacards_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_BDT_SM_HbbFat_WjjFat_HP_e.root
"""
<ggHHsamplename>_<whatever>_Hbb_HZZ
<ggHHsamplename>_<whatever>_Hbb_Htt
"""
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where prepareDatacards.root are ")
parser.add_option("--card",      type="string", dest="card",      help="name of prepareDatacards.root. In not given will pick all from the inputPath", default="none")
(options, args) = parser.parse_args()

inputPath = options.inputPath
card      = options.card

info_channel = {
    # name on prepareDatacard    : name to change
    "EWK"                     : "DY",
    "signal_ggf_nonresonant_" : "ggHH_",
    "signal_vbf_nonresonant_" : "qqHH_",
    "TTH"                     : "ttH_hww",
    "TH"                      : "tHW_hww",
    "VH"                      : "WH_hww",
}

info_coupling = {
    # name on prepareDatacard    : name to change
    "cHHH0"                   : "kl_0_kt_1",
    "cHHH1"                   : "kl_1_kt_1",
    "cHHH2p45"                : "kl_2p45_kt_1",
    "cHHH5"                   : "kl_5_kt_1",
    "1_1_1"                   : "CV_1_C2V_1_kl_1",
    "1_1_2"                   : "CV_1_C2V_1_kl_2",
    "1_2_1"                   : "CV_1_C2V_2_kl_1",
    "1_1_0"                   : "CV_1_C2V_1_kl_0",
    "1p5_1_1"                 : "CV_1p5_C2V_1_kl_1",
    "0p5_1_1"                 : "CV_0p5_C2V_1_kl_1",
}

info_brs = OrderedDict()
info_brs["bbvv_sl"] = "SL_hbb_hww"
info_brs["bbvv"]    = "DL_hbb_hww"
info_brs["bbtt"]    = "hbb_htt"

info_brs_remains = OrderedDict()
info_brs_remains["DL_hbb_hww_sl"] = "SL_hbb_hww"
info_brs_remains["TtHW_hww"] = "ttH_hww"

def rename_procs (inputShapesL, info_channelL, info_brsL, info_couplingL, info_brs_remainsL) :
    ## it assumes no subdirectories in the preparedatacards file,
    tfileout1 = ROOT.TFile(inputShapesL, "UPDATE")
    tfileout1.cd()
    for nkey, key in enumerate(tfileout1.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        #if type(obj) is not ROOT.TH1F and type(obj) is not ROOT.TH1D and type(obj) is not ROOT.TH1 and type(obj) is not ROOT.TH1S and type(obj) is not ROOT.TH1C and type(obj) is not ROOT.TH1 :
        if type(obj) is not ROOT.TH1F :
            if type(obj) is ROOT.TH1 :
                print ("data_obs can be be TH1")
                continue
            else :
                print ("WARNING: All the histograms that are not data_obs should be TH1F - otherwhise combine will crash!!!")
                sys.exit()
        nominal  = ROOT.TH1F()
        for proc in info_channelL.keys() :
            if proc in obj_name:
                nominal = obj.Clone()
                nominal.SetName( obj_name.replace(proc, info_channelL[proc]) )
                print ( "replaced channel %s by %s" % (obj_name, obj_name.replace(proc, info_channelL[proc]) ) )
        for proc in info_couplingL.keys() :
            if proc in obj_name:
                nominal = obj.Clone()
                nominal.SetName( obj_name.replace(proc, info_couplingL[proc]) )
                print ( "replaced coupling %s by %s" % (obj_name, obj_name.replace(proc, info_couplingL[proc]) ) )
        for proc in info_brsL.keys() :
            if proc in obj_name:
                nominal = obj.Clone()
                nominal.SetName( obj_name.replace(proc, info_brsL[proc]) )
                print ( "replaced decay mode name %s by %s" % (obj_name, obj_name.replace(proc, info_brsL[proc]) ) )
        for proc in info_brs_remains.keys() :
            if proc in obj_name:
                nominal = obj.Clone()
                nominal.SetName( obj_name.replace(proc, info_brs_remains[proc]) )
                print ( "replaced decay mode name %s by %s" % (obj_name, obj_name.replace(proc, info_brs_remains[proc]) ))
        nominal.Write()
    tfileout1.Close()

inputPathNew = "%s/newProcName/" % inputPath
try :
    os.mkdir( inputPathNew )
except :
    print ("already exists: ", inputPathNew)
print ("\n copied \n %s to \n %s \nto have cards with renamed processes" % (inputPath, inputPathNew))

if card == "none" :
    listproc = glob.glob( "%s/*.root" % inputPath)
else :
    listproc = [ "%s/%s" % (inputPath, card) ]

for prepareDatacard in listproc :
    prepareDatacardNew = prepareDatacard.replace(inputPath, inputPathNew)
    shutil.copy2(prepareDatacard, prepareDatacardNew)
    print ("done", prepareDatacardNew)
    rename_procs(prepareDatacardNew, info_channel, info_brs, info_coupling, info_brs_remains)
