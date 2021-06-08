#!/usr/bin/env python
import os, shlex
from subprocess import Popen, PIPE
import glob
import shutil
import ROOT
import re
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

info_syst = {
    "HH_Up": "HHUp", 
    "HH_Down": "HHDown", 
}

info_channel = {
    # name on prepareDatacard    : name to change
    #"EWK"                     : "DY",
    "signal_ggf_nonresonant_" : "ggHH_",
    "signal_vbf_nonresonant_" : "qqHH_",
    "data_fakes"              : "Fakes",
    #"data_DY"              : "DY",
    "TTH"                     : "ttH",
    "TTZ"                     : "ttZ",
    "TTW"                     : "ttW",
    #"TTH"                     : "ttH_hww",
    #"TH"                      : "tHW_hww",
    #"VH"                      : "WH_hww",
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
info_brs["bbww"] = "hbbhww"
info_brs["bbzz"] = "hbbhzz"
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
#info_brs_remains["TtHW_hww"] = "ttH_hww"
info_brs_remains["_hh_"] = "_"
VV_process = ["qqZZ", "WZ", "ggZZ", "WW"]
Other = ["Convs", "Other", "TTZ", "TTW", "TTWW"]
#Other = ["Convs", "Other"] 
exclude_proc = re.compile('({})'.format('|'.join(VV_process + Other)))
all_syst = ["", "JES", "JER", "lepEff_eltight", "lepEff_mutight", "lepEff_elloose", "lepEff_muloose", "UnclusteredEn", "btag_HF", "btag_HFStats1", "btag_HFStats2", "btag_LF", "btag_LFStats1", "btag_LFStats2", "btag_cErr1", "btag_cErr2", "btag_JES", "pileup", "l1PreFire", "AK8JMS", "AK8JMR", "AK8JER", "puJetIDEff", "puJetIDMistag", "lepEff_eltightRecomp", "lepEff_mutightRecomp", "tauES", "trigger_1lE", "trigger_1lMu", "trigger_2lssEE", "trigger_2lssEMu", "trigger_2lssMuMu", "thu_shape", "TT_ISR", "TT_FSR", "topPtReweighting"]
JES = ["JESAbsolute", "JESAbsolute_Era", "JESBBEC1", "JESBBEC1_Era", "JESEC2", "JESEC2_Era", "JESFlavorQCD", "JESHF", "JESHF_Era", "JESRelativeBal", "JESRelativeSample_Era"]
AK8JES = []
for syst in JES:
    AK8syst = syst.replace("JES", "AK8JES")
    AK8JES.append(AK8syst)
all_syst.extend(JES)
all_syst.extend(AK8JES)
# info_brs_remains["hh_htautauhww"] = "htautauhww"
# info_brs_remains["hh_hzzhzz"] = "hzzhzz"
# info_brs_remains["hh_htautauhzz"] = "htautauhzz"
# info_brs_remains["hh_hwwhww"] = "hwwhww"
# info_brs_remains["hh_hzzhww"] = "hzzhww"
# info_brs_remains["hh_htautauhtautau"] = "htautauhtautau"
def check_otherhist(file, name, process):
    for proc in process:
        hist = file.Get(name)
        if hist:
            return True
    return False

def merge_process(tfileout1, tfileout2, process, merge):
    print tfileout1.GetListOfKeys()
    for syst in all_syst:
        for updn in ["Up", "Down"]:
            if syst == "" and updn == "Down":
                continue
            found = False
            for  proc in process:
                if syst == "":
                    name = "%s" %(proc)
                elif syst == 'thu_shape':
                    if name.find('TTH_h') != -1:
                        name = "%s_CMS_ttHl_%s_%s%s" %(proc, syst, 'ttH', updn)
                    elif name.find('TH_h') != -1:
                        name = "%s_CMS_ttHl_%s_%s%s" %(proc, syst, 'tHq', updn)
                    else:
                        name = "%s_CMS_ttHl_%s_%s%s" %(proc, syst, proc, updn)
                else:
                    name = "%s_CMS_ttHl_%s%s" %(proc, syst, updn)
                h = tfileout1.Get(name)
                if not h:
                    if check_otherhist(tfileout1, name, list(set(process)-set([proc]))):
                        h = tfileout1.Get(proc)
                        print 'considering %s as up/dn variation as %s is absent' %(proc, syst)
                    elif syst == 'thu_shape':
                        h = tfileout1.Get(proc)
                        print proc, '\t', h
                        print 'considering %s as up/dn variation as %s is absent' %(proc, syst)
                    else:
                        continue
                if not found:
                    hadd = ROOT.TH1F("", "", h.GetNbinsX(), h.GetBinLowEdge(1), h.GetBinLowEdge(h.GetNbinsX())+h.GetBinWidth(h.GetNbinsX()))
                    hadd.Sumw2()
                    hadd.Add(h)
                    print 'found ', name
                    found = True
                else:
                    print 'adding ', h.GetName()
                    hadd.Add(h)
                del h
            if not found:
                print 'not found ', syst, '\t in process ', process
            if found:
                if syst == "":
                    hadd.SetName(merge)
                    hadd.SetTitle(merge)
                elif syst == 'thu_shape':
                    hadd.SetName("%s_CMS_ttHl_%s_%s%s" %(merge, syst, merge, updn))
                    hadd.SetTitle("%s_CMS_ttHl_%s_%s%s" %(merge, syst, merge, updn))
                else:
                    hadd.SetName("%s_CMS_ttHl_%s%s" %(merge, syst, updn))
                    hadd.SetTitle("%s_CMS_ttHl_%s%s" %(merge, syst, updn))
                tfileout2.cd()
                hadd.Write()
                del hadd
            tfileout1.cd()

def rename_procs (inputShapesL,inputShapesLnew ,info_channelL, info_brsL, info_couplingL, info_brs_remainsL, info_syst) :
    ## it assumes no subdirectories in the preparedatacards file,
    tfileout1 = ROOT.TFile(inputShapesL, "UPDATE")
    tfileout2 = ROOT.TFile(inputShapesLnew, "RECREATE")
    merge_process(tfileout1, tfileout2, Other, "Other_bbWW")
    #merge_process(tfileout1, tfileout2, VV_process, "VV")
    tfileout1.cd()

    for nkey, key in enumerate(tfileout1.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        if exclude_proc.search(obj_name): continue
        #if type(obj) is not ROOT.TH1F and type(obj) is not ROOT.TH1D and type(obj) is not ROOT.TH1 and type(obj) is not ROOT.TH1S and type(obj) is not ROOT.TH1C and type(obj) is not ROOT.TH1 :
        if type(obj) is not ROOT.TH1F :
            if type(obj) is ROOT.TH1 :
                print ("data_obs can be be TH1")
                continue
            else :
                print ("WARNING: All the histograms that are not data_obs should be TH1F - otherwhise combine will crash!!!")
                sys.exit()
        #nominal  = ROOT.TH1F()
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
        for proc in info_brs_remains.keys():
            if proc in obj_newname and '_hh_CMS' not in obj_newname:
                print ( "replaced decay mode remnant %s by %s" % (obj_newname, obj_newname.replace(proc, info_brs_remains[proc]) ) )
                obj_newname = obj_newname.replace(proc, info_brs_remains[proc])
        if obj_name == "W":
            obj_newname = "WJets"
        if obj_name.find("W_CMS") != -1 and 'TTW' not in obj_name and 'WW' not in obj_name and obj_name.startswith("W_CMS"):
            obj_newname = obj_newname.replace("W_", "WJets_")
            
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
    #shutil.copy2(prepareDatacard, prepareDatacardNew)
    #print ("done", prepareDatacardNew)
    rename_procs(prepareDatacard, prepareDatacardNew, info_channel, info_brs, info_coupling, info_brs_remains, info_syst)
