#!/usr/bin/env python
import os, shlex
from subprocess import Popen, PIPE
import glob
import shutil
import ROOT
from collections import OrderedDict

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where prepareDatacards.root are ")
parser.add_option("--card",      type="string", dest="card",      help="name of prepareDatacards.root. In not given will pick all from the inputPath", default="none")
parser.add_option("--analysis",      type="string", dest="analysis",      help="Name of the analysis to allow for custom proccesses i.e. multilepton_data_fakes", default="multilepton")
(options, args) = parser.parse_args()

inputPath = options.inputPath
card      = options.card
analysis      = options.analysis

#Propably unnecesary by now
info_syst = {
    "HH_Up": "HHUp", 
    "HH_Down": "HHDown", 
}

info_channel = {
    # name on prepareDatacard    : name to change
    "signal_ggf_nonresonant_" : "ggHH_",
    "signal_vbf_nonresonant_" : "qqHH_",
    "TTH"                    : "ttH",
    "data_fakes"              : "%s_data_fakes"%analysis,
    "data_flips"              : "%s_data_flips"%analysis,
    "Convs"                   : "%s_Convs"%analysis,
    "Other"                   : "%s_Other"%analysis,
    "fakes_mc"                : "%s_fakes_mc"%analysis,
    "flips_mc"                : "%s_flips_mc"%analysis,
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
    "1_0_1"                   : "CV_1_C2V_0_kl_1",
}

info_brs = OrderedDict()
info_brs["bbvv_sl"] = "SL_hbb_hww"
info_brs["bbvv"]    = "DL_hbb_hww"
info_brs["bbtt"]    = "hbbhtt"
info_brs["ttww"] = "htthww"
info_brs["zzzz"] = "hzzhzz"
info_brs["ttzz"] = "htthzz"
info_brs["wwww"] = "hwwhww"
info_brs["zzww"] = "hzzhww"
info_brs["tttt"] = "htthtt"
info_brs_remains = OrderedDict()
info_brs_remains["DL_hbb_hww_sl"] = "SL_hbb_hww"
info_brs_remains["_hh_"] = "_"

def rename_procs (inputShapesL,inputShapesLnew ,info_channelL, info_brsL, info_couplingL, info_brs_remainsL, info_syst) :
    ## it assumes no subdirectories in the preparedatacards file,
    tfileout1 = ROOT.TFile(inputShapesL, "UPDATE")
    tfileout2 = ROOT.TFile(inputShapesLnew, "RECREATE")
    tfileout1.cd()

    for nkey, key in enumerate(tfileout1.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        if type(obj) is not ROOT.TH1F :
            if type(obj) is ROOT.TH1 :
                print ("data_obs can be be TH1")
                continue
            else :
                print ("WARNING: All the histograms that are not data_obs should be TH1F - otherwhise combine will crash!!!")
                sys.exit()
        obj_newname = obj_name
        
        for proc in info_syst.keys() :
            if proc in obj_name:
                print ( "replaced syst %s by %s" % (obj_newname, obj_newname.replace(proc, info_syst[proc]) ) )
                obj_newname = obj_newname.replace(proc, info_syst[proc])
        for proc in info_channelL.keys() :
            if proc in obj_name:
                print ( "replaced channel %s by %s" % (obj_newname, obj_newname.replace(proc, info_channelL[proc]) ) )
                obj_newname = obj_newname.replace(proc, info_channelL[proc])
        for proc in info_couplingL.keys() :
            if proc in obj_name:
                print ( "replaced coupling %s by %s" % (obj_newname, obj_newname.replace(proc, info_couplingL[proc]) ) )
                obj_newname = obj_newname.replace(proc, info_couplingL[proc])
        for proc in info_brsL.keys() :
            if proc in obj_name:
                print ( "replaced decay mode %s by %s" % (obj_newname, obj_newname.replace(proc, info_brsL[proc]) ) )
                obj_newname = obj_newname.replace(proc, info_brsL[proc])
        for proc in info_brs_remains.keys() :
            if proc in obj_newname:
                print ( "replaced decay mode remnant %s by %s" % (obj_newname, obj_newname.replace(proc, info_brs_remains[proc]) ) )
                obj_newname = obj_newname.replace(proc, info_brs_remains[proc])
        tfileout2.cd()
        nominal = obj.Clone()
        nominal.SetName( obj_newname )
        nominal.Write()
        tfileout1.cd()
    tfileout1.Close()
    tfileout2.Close()

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
    rename_procs(prepareDatacard, prepareDatacardNew, info_channel, info_brs, info_coupling, info_brs_remains, info_syst)
