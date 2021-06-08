#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import ROOT
import shutil
import sys, os, re, shlex
from subprocess import Popen, PIPE

import os.path
from os import path

from CombineHarvester.ttH_htt.data_manager import manipulate_cards, lists_overlap, construct_templates, list_proc, make_threshold, checkSyst, check_integral, check_systematics, rescale_stxs_pT_bins, filter_lowYieldProcs, filterSig, filter_genuineShape
sys.stdout.flush()

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputShapes",    type="string",       dest="inputShapes", help="Full path of prepareDatacards.root")
parser.add_option("--channel",        type="string",       dest="channel",     help="Channel to assume (to get the correct set of syst)")
parser.add_option("--cardFolder",     type="string",       dest="cardFolder",  help="Folder where to save the datacards (relative or full).\n Default: teste_datacards",  default=".")
parser.add_option("--analysis",       type="string",       dest="analysis",    help="Analysis type = 'ttH' or 'HH' (to know what to take as Higgs procs and naming convention of systematics), Default ttH", default="ttH")
parser.add_option("--output_file",    type="string",       dest="output_file", help="Name of the output file.\n Default: the same of the input, substituing 'prepareDatacards' by 'datacard' (+ the coupling if the --couplings is used)", default="none")
parser.add_option("--coupling",       type="string",       dest="coupling",    help="Coupling to take in tH.\n Default: do for SM, do not add couplings on output naming convention", default="none")
parser.add_option("--shapeSyst",      action="store_true", dest="shapeSyst",   help="Do apply the shape systematics. Default: False", default=False)
parser.add_option("--noX_prefix",     action="store_true", dest="noX_prefix",  help="do not assume hist from prepareDatacards starts with 'x_' prefix", default=False)
parser.add_option("--only_ttH_sig",   action="store_true", dest="only_ttH_sig",help="consider only ttH as signal on the datacard -- for single channel tests", default=False)
parser.add_option("--only_tHq_sig",   action="store_true", dest="only_tHq_sig",help="consider only ttH as signal on the datacard -- for single channel tests", default=False)
parser.add_option("--only_BKG_sig",   action="store_true", dest="only_BKG_sig",help="consider only ttH as signal on the datacard -- for single channel tests", default=False)
parser.add_option("--use_Exptl_HiggsBR_Uncs",   action="store_true", dest="use_Exptl_HiggsBR_Uncs",help="Use the exprimental measured Higgs BR Unc.s instead of theoretical ones", default=False)
parser.add_option("--no_data",        action="store_true", dest="no_data",     help="Do not read data_obs, fill it as it would be the sum of the processes (some combine checks ask for it)", default=False)
parser.add_option("--fake_mc",        action="store_true", dest="fake_mc",     help="Use fakes and flips from MC", default=False)
parser.add_option("--era",            type="int",          dest="era",         help="Era to consider (important for list of systematics). Default: 2017",  default=2017)
parser.add_option("--tH_kin",         action="store_true", dest="tH_kin",      help="Cards for studies with tH kinematics have specifics", default=False)
parser.add_option("--HH_kin",         action="store_true", dest="HH_kin",      help="Cards for studies with HH kinematics have specifics", default=False)
parser.add_option("--stxs",           action="store_true", dest="stxs",        help="Cards for stxs", default=False)
parser.add_option("--forceModifyShapes",           action="store_true", dest="forceModifyShapes",        help="if file with modified shapes exist, delete it.", default=False)

parser.add_option("--signal_type",    type="string",       dest="signal_type", help="Options: \"nonresLO\" | \"nonresNLO\" | \"res\" ", default="none")
parser.add_option("--mass",           type="string",       dest="mass",        help="Options: \n nonresNLO = it will be ignored \n noresLO = \"SM\", \"BM12\", \"kl_1p00\"... \n \"spin0_900\", ...", default="none")
parser.add_option("--HHtype",         type="string",       dest="HHtype",      help="Options: \"bbWW\" | \"multilepton\" | \"bbWW_bbtt\" ", default="none")
parser.add_option("--renamedHHInput", action="store_true", dest="renamedHHInput",   help="If used input already renamed.", default=True)
parser.add_option("--isCR", action="store_true", dest="isCR",   help="If datacard is created for an CR.", default=False)
parser.add_option("--withCR", action="store_true", dest="withCR",   help="If datacard is created for use with CR.", default=False)
parser.add_option("--binByBin", action="store_true", dest="binByBin",   help="If direct bin per bin uncertainties shouzld be used instead of autoMC stats", default=False)
parser.add_option("--subcat",    type="string",       dest="subcat", help="subcategory to be considered for proceeses to remove ", default="")
parser.add_option("--removeLowYieldShapes",        action="store_true", dest="removeLowYieldShapes",     help="Weather to aplly shape systematics for low Yield bkg or not", default=False)
parser.add_option("--removeLowImpactShapes",        action="store_true", dest="removeLowImpactShapes",     help="Weather to remove shapes with small norm/shape effects or not", default=False)
parser.add_option("--dataMCagreement",        action="store_true", dest="dataMCagreement",     help="write datacard only to check data mc ageement", default=False)
(options, args) = parser.parse_args()

inputShapesRaw = options.inputShapes
inputShapes = inputShapesRaw.replace(".root", "_mod.root")
channel     = options.channel
era         = options.era
binByBin = options.binByBin
shape       = options.shapeSyst
analysis    = options.analysis
cardFolder  = options.cardFolder
coupling    = options.coupling
noX_prefix  = options.noX_prefix
only_ttH_sig = options.only_ttH_sig
only_tHq_sig = options.only_tHq_sig
only_BKG_sig = options.only_BKG_sig
fake_mc      = options.fake_mc
no_data      = options.no_data
stxs         = options.stxs
tH_kin       = options.tH_kin
HH_kin       = options.HH_kin
signal_type  = options.signal_type
mass         = options.mass
HHtype       = options.HHtype
removeLowYieldShapes = options.removeLowYieldShapes
removeLowImpactShapes = options.removeLowImpactShapes
use_Exptl_HiggsBR_Uncs = options.use_Exptl_HiggsBR_Uncs
forceModifyShapes      = options.forceModifyShapes
renamedHHInput         = options.renamedHHInput
isCR = options.isCR
withCR = options.withCR
subcat = options.subcat
dataMCagreement = options.dataMCagreement
# output the card
if options.output_file == "none" :
    output_file = (cardFolder + "/" + str(os.path.basename(inputShapes)).replace(".root","").replace("prepareDatacards", "datacard")).replace("addSystFakeRate","datacard")
else :
    output_file =   options.output_file

if use_Exptl_HiggsBR_Uncs:
    print("Using Experimental Unc.s on Higgs BRs")
else:
    print("Using Theoretical Unc.s on Higgs BRs")

if not os.path.exists(cardFolder):
    os.makedirs(cardFolder)


if analysis == "ttH" :
    info_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_channels.py"
    execfile(info_file)
    print ("list of signals/bkgs by channel taken from: %s" % info_file)
    print ("syst values and channels options taken from: %s " % syst_file)
    syst_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_syst.py"
    execfile(syst_file)
elif analysis == "HH" :
    info_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_channels_HH.py"
    execfile(info_file)
    print ("list of signals/bkgs by channel taken from: %s" % info_file)
    syst_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_syst_HH.py"
    execfile(syst_file)
    print ("syst values and channels options taken from: %s " % syst_file)
else :
    print ("Analysis %s not implemented, should be \"ttH\" or \"HH\"")
    sys.exit()

higgs_procs = list_channels( fake_mc, signal_type, mass, HHtype, renamedHHInput )["higgs_procs"]
if (isCR): higgs_procs = []
list_channel_opt   = list_channels( fake_mc, signal_type, mass, HHtype, renamedHHInput )["info_bkg_channel"]
bkg_proc_from_data = list_channel_opt[channel]["bkg_proc_from_data"]
bkg_procs_from_MC  = list_channel_opt[channel]["bkg_procs_from_MC"]
'''if dataMCagreement:
    add_proc = []
    higgs_procs = []
    for proc in bkg_procs_from_MC:
        for hbr in ['hbbhww', 'hbbhtt', 'hbbhzz', '_hww', '_hbb', '_hzz', '_htt']:
            if hbr in proc:
                bkg_procs_from_MC.remove(proc)
                proc = proc.replace(hbr, '')
                add_proc.append(proc)
    print '*************', add_proc
    bkg_procs_from_MC.extend(add_proc)
    print bkg_procs_from_MC'''
# if a coupling is done read the tH signal with that coupling on naming convention
if not (coupling == "none" or coupling == "kt_1_kv_1"):
    higgs_procs = [ [ entry.replace("tHq_", "tHq_%s_" % coupling).replace("tHW_", "tHW_%s_" % coupling) for entry in entries ] for entries in higgs_procs ]
higgs_procs_plain = sum(higgs_procs,[])

print ("higgs_procs_plain", higgs_procs_plain)

if only_ttH_sig :
    print ("MC processes -- after chosing to mark as signal only ttH:")
    bkg_procs_from_MC += [ entry for entry in higgs_procs_plain if "ttH_" not in  entry]
    higgs_procs        = [ entries for entries in higgs_procs if "ttH_" in entries[0] ]
    print ("BKG from MC   (new): ", bkg_procs_from_MC)
    print ("signal        (new): ", higgs_procs)
    higgs_procs_plain = sum(higgs_procs,[])
elif only_tHq_sig :
    print ("MC processes -- after chosing to mark as signal only ttH:")
    bkg_procs_from_MC += [ entry for entry in higgs_procs_plain if "tHq_" not in  entry]
    higgs_procs        = [ entries for entries in higgs_procs if "tHq_" in entries[0] ]
    print ("BKG from MC   (new): ", bkg_procs_from_MC)
    print ("signal        (new): ", higgs_procs)
    higgs_procs_plain = sum(higgs_procs,[])
elif only_BKG_sig :
    print ("MC processes -- after chosing to mark as signal only ttH:")
    bkg_procs_from_MC = [ entry for entry in bkg_procs_from_MC if not "TTW" in entry and not "TTZ" in entry ]
    bkg_procs_from_MC += sum(higgs_procs,[])
    print ("BKG from MC   (new): ", bkg_procs_from_MC)
    print ("signal        (new): ", ["TTW", "TTZ"])
    higgs_procs_plain = ["TTW", "TTZ"] #higgs_procs

if tH_kin :
    print ("HH should not be marked as process")
    bkg_procs_from_MC += [ entry for entry in higgs_procs_plain if "HH" in  entry]
    higgs_procs        = [ entries for entries in higgs_procs if not "HH" in entries[0] ]
    print ("BKG from MC   (new): ", bkg_procs_from_MC)
    print ("signal        (new): ", higgs_procs)
    higgs_procs_plain = sum(higgs_procs,[])
removeProcs = True
try :
    print ( "proc_to_remove: listed by hand in configs/list_channels.py" )
    print (list_channel_opt[channel]["proc_to_remove"][str(era)][subcat])
except :
    removeProcs = False
    print ( "do not remove any process listed by hand" )

#removeProcslist = check_integral(inputShapesRaw, analysis)
if removeProcs:
    removeProcslist = list_channel_opt[channel]["proc_to_remove"][str(era)][subcat]
    if not (coupling == "none" or coupling == "kt_1_kv_1") :
        removeProcslist = [nn.replace("tHq_", "tHq_%s_" % coupling).replace("tHW_", "tHW_%s_" % coupling) for nn in list(removeProcslist) if "tHW" in nn or "tHq" in nn]
    if len(removeProcslist) > 0 :
        print("Removing processes where integral is below certain threshold" + str(removeProcslist))
        higgs_procs_plain = list(set(list(higgs_procs_plain)) - set(list(removeProcslist)))
        print ("New list of Higgs processes", higgs_procs_plain)
        print ("Removed", str(removeProcslist))
        bkg_procs_from_MC = list(set(list(bkg_procs_from_MC)) - set(list(removeProcslist)))
        print ("New list of bkg processes", bkg_procs_from_MC)
        print ("Removed", str(removeProcslist))

pT_bins = {}
if stxs :
    # take ttH_ as the pT bins
    stxs_pT_bins            = {
        # pT bin           XS (now the cards are done normalizing ttH in each pT bin is normalized to 1pb)
        "PTH_fwd"       : {2016 : 0.002646, 2017 : 0.002486, 2018 : 0.002732},
        "PTH_0_60"      : {2016 : 0.048411, 2017 : 0.047804, 2018 : 0.047128},
        "PTH_60_120"    : {2016 : 0.074606, 2017 : 0.074574, 2018 : 0.073956},
        "PTH_120_200"   : {2016 : 0.053548, 2017 : 0.053988, 2018 : 0.054276},
        "PTH_200_300"   : {2016 : 0.022305, 2017 : 0.022525, 2018 : 0.022999},
        "PTH_300_infty" : {2016 : 0.010284, 2017 : 0.010420, 2018 : 0.010711},
        #"PTH_300_450"   : {2016 : 0.008042, 2017 : 0.008178, 2018 : 0.008397},
        #"PTH_300_infty" : {2016 : 0.002241, 2017 : 0.002242, 2018 : 0.002314},
    }
    for xproc in higgs_procs_plain :
      if "ttH_" in xproc :
        # remove the ttH_br of the list and add the same in a list of pT bins
        higgs_procs_plain        = list(set(higgs_procs_plain) - set([xproc]))
        for pTs in list(stxs_pT_bins.keys()) :
          higgs_procs_plain   = higgs_procs_plain + [ xproc.replace("ttH", "ttH_" + pTs) ]
    print ("higgs_procs == ", higgs_procs_plain)

if shape :
    print ("Do not allow Zero shape systematics variations")
    inputShapes = inputShapesRaw.replace(".root", "_mod.root")
    if forceModifyShapes :
        if path.exists(inputShapes) :
            print("Deleting: ", inputShapes)
            os.remove(inputShapes)

    if not path.exists(inputShapes) :
        print("inputShapes = ", inputShapes)
        shutil.copy2(inputShapesRaw, inputShapes)
        #if stxs :
        #    print ("\n copied \n %s to \n %s \nto rescale the pT bins with the cross sections by pT bins (see this git issue https://github.com/HEP-KBFI/tth-htt/issues/142)" % (inputShapesRaw, inputShapes))
        #    rescale_stxs_pT_bins(inputShapes, stxs_pT_bins, era)
        #else :
        #    print ("\n copied \n %s to \n %s \nto make modifications in problematic bins." % (inputShapesRaw, inputShapes))
        #    # FIXME: now if we do rescale_stxs_pT_bins somehow doing check_systematics makes the result without correct rescaling.
        #    # I will not debug that now, the check_systematics is mostly to not deliver weird postfit shapes
        #    # with bins with large uncertainties, it does not matter for numeric results.
        #    check_systematics(inputShapes, coupling)
        if analysis == "ttH":
            check_systematics(inputShapes, coupling)
        else:
            check_systematics(inputShapes, coupling, analysis, True)
    else :
        print ("file %s already modified" % inputShapes)
else :
    inputShapes = inputShapesRaw

if analysis!="ttH":
    higgs_procs_plain = filterSig(inputShapes,higgs_procs_plain, 0.001)


# check a threshold on processes
print ("do not add a process to datacard if the yield is smaller than 0.01 -- if so, do not add it")
bkg_proc_from_data = make_threshold(0.01, bkg_proc_from_data,  inputShapes, tH_kin)
bkg_procs_from_MC  = make_threshold(0.01, bkg_procs_from_MC, inputShapes, tH_kin)
'''if analysis == "HH" and signal_type == "nonresLO":
    ## FIXME: to the ggHH and qqHH processes in NLO cards do not discard any component by threshold
    # by now it is not discarting any H process, narrow that down to ggHH and qqHH processes
    higgs_procs_plain  = make_threshold(0.01, higgs_procs_plain, inputShapes, tH_kin)'''

print ("final list of signal/bkg to add to datacards")
MC_proc = higgs_procs_plain + bkg_procs_from_MC
print ("MC processes:")
print ("BKG from MC  (original)  : ", bkg_procs_from_MC)
print ("BKG from data (original) : ", bkg_proc_from_data)
print ("signal        (original): ", higgs_procs_plain)

specific_syst_list = specific_syst(analysis, list_channel_opt, HHtype)
print("analysis type        :", analysis)

############
bkg_procs_lowYield = []
if removeLowYieldShapes:
    bkg_procs_lowYield = filter_lowYieldProcs(inputShapes,bkg_proc_from_data+bkg_procs_from_MC)
#############


###########################################
# start the list of common systematics for all channels
###########################################

cb = ch.CombineHarvester()
cats = [
    (1, "%s_%s" % (analysis, channel))
    ]
masses = ["*"]
if not no_data :
    cb.AddObservations(["*"], ["%sl" % analysis], ["13TeV"], ["*"], cats)
cb.AddProcesses(    ['*'], [''], ['13TeV'], [''], bkg_proc_from_data + bkg_procs_from_MC, cats, False)
cb.AddProcesses(    ['*'], [''], ['13TeV'], [''], higgs_procs_plain, cats, True)

#######################################
print ("Adding lumi syt uncorrelated/year")
# check if we keep the lumis/era correlated or not
cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_%s" % str(era), "lnN", ch.SystMap()(lumiSyst[era]))
if (analysis != "ttH"):
    cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_2016_2017_2018", "lnN", ch.SystMap()(lumi_2016_2017_2018[era]))
    if era in [2017, 2018] :
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_2017_2018",  "lnN", ch.SystMap()(lumi_2017_2018[era]))
    if era in [2017, 2016] :
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_2016_2017", "lnN", ch.SystMap()(lumi_2016_2017[era]))
else:
    cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_XY", "lnN", ch.SystMap()(lumi_2016_2017_2018[era]))
    if era in [2017, 2018] :
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_LS",  "lnN", ch.SystMap()(lumi_2017_2018[era]))
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_BCC", "lnN", ch.SystMap()(lumi_13TeV_BCC[era]))
    if era in [2017, 2016] :
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_BBD", "lnN", ch.SystMap()(lumi_2016_2017[era]))
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_DB",  "lnN", ch.SystMap()(lumi_13TeV_DB[era]))
        cb.cp().process(bkg_procs_from_MC + higgs_procs_plain).AddSyst(cb, "CMS_lumi_13TeV_GS",  "lnN", ch.SystMap()(lumi_13TeV_GS[era]))

#######################################
# FIXME: one of the syst is logUniform -- fix
if 0 > 1 : # FIXME: remind why we added that at some point
    # it can be done as text modification afterwards
    print ("Adding rateParam")
    # normalizations floating individually (ttWW correlated with ttW and among signal types)
    # not relevant if you do the fit expliciting things on the text2ws maker -- but it does not hurt
    for proc in bkg_procs_from_MC  :
        if "TTWW" in proc :
            cb.cp().process([proc]).AddSyst(cb, 'scale_TTWW', 'rateParam', ch.SystMap()(("(@0)", "scale_TTW")))
            print ("process: " + proc + " is proportonal to TTW")
        else :
            cb.cp().process([proc]).AddSyst(cb, "scale_%s" % proc, 'rateParam', ch.SystMap()(1.0))
            print ("added rateparam to: " + proc)

    # correlate the rateparam among the Higgs processes
    for hsig in higgs_procs :
        for br, hsbr in enumerate(hsig) :
            if br == 0 :
                cb.cp().process([hsbr]).AddSyst(cb, "scale_%s" % hsbr, 'rateParam', ch.SystMap()(1.0))
                print ("added rateparam to: " + hsbr)
            else :
                cb.cp().process([proc]).AddSyst(cb, 'scale_%s' % hsbr, 'rateParam', ch.SystMap()(("(@0)", "scale_%s" % hsig[0])))
                print ("process: " + hsbr + " is proportonal to", hsig[0])

########################################
#add Clos_e_norm and Clos_m_norm for multilepton as lnN
if (analysis != "ttH") and (not isCR) and  HHtype=="multilepton":
    if channel in Clos_m_norm_ln_Syst.keys():
        cb.cp().process(["multilepton_data_fakes"]).AddSyst(cb,  "CMS_multilepton_Clos_m_norm_%s_%s"%(str(era),channel), "lnN", ch.SystMap()(Clos_m_norm_ln_Syst[channel][str(era)]))
        print ("added CMS_multilepton_Clos_m_norm_%s_%s with value "%(str(era),channel) + str(Clos_m_norm_ln_Syst[channel][str(era)]) + " to processes: ", ["multilepton_data_fakes"])
    if channel in Clos_e_norm_ln_Syst.keys():
        cb.cp().process(["multilepton_data_fakes"]).AddSyst(cb,  "CMS_multilepton_Clos_e_norm_%s_%s"%(str(era),channel), "lnN", ch.SystMap()(Clos_e_norm_ln_Syst[channel][str(era)]))
        print ("added CMS_multilepton_Clos_e_norm_%s_%s with value "%(str(era),channel) + str(Clos_e_norm_ln_Syst[channel][str(era)]) + " to processes: ", ["multilepton_data_fakes"])
    else:
        print ("Skipping CMS_multilepton_Clos_e_norm_ERA_CHANNEL as channel is %s"%channel)
        print ("Skipping CMS_multilepton_Clos_m_norm_ERA_CHANNEL as channel is %s"%channel)
########################################
# add vbf dipole recoile uncertainties #FIXME bbWW implementation
if (analysis != "ttH") and (not isCR) and  HHtype=="multilepton":
    wwww_procs = []
    ttww_procs = []
    tttt_procs = []
    ttzz_procs = []
    zzww_procs = []
    zzzz_procs = []
    for pr in higgs_procs_plain:
        if not ("qqHH" in pr or "signal_vbf_nonresonant" in pr):
            continue
        if "wwww" in pr or "hwwhww" in pr:
            wwww_procs.append(pr)
        if "ttww" in pr or "htthww" in pr:
            ttww_procs.append(pr)
        if "tttt" in pr or "htthtt" in pr:
            tttt_procs.append(pr)
        if "ttzz" in pr or "htthzz" in pr:
            ttzz_procs.append(pr)
        if "zzww" in pr or "hzzhww" in pr:
            zzww_procs.append(pr)
        if "zzzz" in pr or "hzzhzz" in pr:
            zzzz_procs.append(pr)
    if len(wwww_procs) >0:
        cb.cp().process(wwww_procs).AddSyst(cb,  "qqHH_pythiaDipoleOn", "lnN", ch.SystMap()((vbf_dipole_ln_Syst[channel]["wwww"],1.)))
        print ("added qqHH_pythiaDipoleOn with value " + str(vbf_dipole_ln_Syst[channel]["wwww"]) + " to processes: ", wwww_procs)
    if len(ttww_procs) >0:
        cb.cp().process(ttww_procs).AddSyst(cb,  "qqHH_pythiaDipoleOn", "lnN", ch.SystMap()((vbf_dipole_ln_Syst[channel]["ttww"],1.)))
        print ("added qqHH_pythiaDipoleOn with value " + str(vbf_dipole_ln_Syst[channel]["ttww"]) + " to processes: ", ttww_procs)
    if len(tttt_procs) >0:
        cb.cp().process(tttt_procs).AddSyst(cb,  "qqHH_pythiaDipoleOn", "lnN", ch.SystMap()((vbf_dipole_ln_Syst[channel]["tttt"],1.)))
        print ("added qqHH_pythiaDipoleOn with value " + str(vbf_dipole_ln_Syst[channel]["tttt"]) + " to processes: ", tttt_procs)
    if len(zzww_procs) >0:
        cb.cp().process(zzww_procs).AddSyst(cb,  "qqHH_pythiaDipoleOn", "lnN", ch.SystMap()((vbf_dipole_ln_Syst[channel]["zzww"],1.)))
        print ("added qqHH_pythiaDipoleOn with value " + str(vbf_dipole_ln_Syst[channel]["zzww"]) + " to processes: ", zzww_procs)
    if len(ttzz_procs) >0:
        cb.cp().process(ttzz_procs).AddSyst(cb,  "qqHH_pythiaDipoleOn", "lnN", ch.SystMap()((vbf_dipole_ln_Syst[channel]["ttzz"],1.)))
        print ("added qqHH_pythiaDipoleOn with value " + str(vbf_dipole_ln_Syst[channel]["ttzz"]) + " to processes: ", ttzz_procs)
    if len(zzzz_procs) >0:
        cb.cp().process(zzzz_procs).AddSyst(cb,  "qqHH_pythiaDipoleOn", "lnN", ch.SystMap()((vbf_dipole_ln_Syst[channel]["zzzz"],1.)))
        print ("added qqHH_pythiaDipoleOn with value " + str(vbf_dipole_ln_Syst[channel]["zzzz"]) + " to processes: ", zzzz_procs)
########################################
# add rate parameters
if withCR and analysis != "ttH" and HHtype=="multilepton":
    cb.cp().process(["WZ"]).AddSyst(cb, 'CMS_multilepton_xsWZ', 'rateParam', ch.SystMap()(("1.0 [0.5/1.5]", "")))
    cb.cp().process(["ggZZ"]).AddSyst(cb, 'CMS_multilepton_xsZZ', 'rateParam', ch.SystMap()(("1.0 [0.5/1.5]", "")))
    cb.cp().process(["qqZZ"]).AddSyst(cb, 'CMS_multilepton_xsZZ', 'rateParam', ch.SystMap()(("1.0 [0.5/1.5]", "")))
########################################

singlehiggs_proc_no_BR = ["TTH", "ttH", "tHq","tHW", "WH","ZH","qqH", "ggH"]
singlehiggs_procs_w_BR = []
for proc in singlehiggs_proc_no_BR:
    singlehiggs_procs_w_BR.append(proc+"_hww")
    singlehiggs_procs_w_BR.append(proc+"_hzz")
    singlehiggs_procs_w_BR.append(proc+"_htt")
    singlehiggs_procs_w_BR.append(proc+"_hbb")
    singlehiggs_procs_w_BR.append(proc+"_hgg")
singlehiggs_procs_w_BR = [SH for SH in singlehiggs_procs_w_BR if SH in bkg_procs_from_MC]

# add theory systematics
for specific_syst in theory_ln_Syst :
    if withCR and analysis != "ttH" and HHtype=="multilepton":
        if "WZ" in specific_syst and "pdf" not in specific_syst:
            continue
        if ("ggZZ" in specific_syst or "ggZZ" in specific_syst) and "pdf" not in specific_syst:
            continue
    procs = theory_ln_Syst[specific_syst]["proc"]
    if len(procs) == 0 :
        continue
    if "HH" in procs[0] and analysis == "ttH":
        for decay in list_channels( fake_mc, signal_type, mass, HHtype, renamedHHInput )["decays_hh"] :
            procs = procs + [procs[0] + decay]
    elif "H" in procs[0] and analysis == "ttH":
        if tH_kin and ("tHq" in procs[0] or "tHW" in procs[0]) :
            continue
        for decay in list_channels( fake_mc, signal_type, mass, HHtype, renamedHHInput )["decays"] :
            procs = procs + [procs[0] + decay]
    if "HH" in procs[0] and analysis == "HH":
        procs_hh = []
        for pr in higgs_procs_plain:
            if procs[0] in pr:
                procs_hh.append(pr)
        procs = procs + procs_hh
    elif "H" in procs[0] and analysis == "HH":
        procs_H = []
        for pr in singlehiggs_procs_w_BR:
            for proc in procs:
                if proc in pr:
                    procs_H.append(pr)
        procs = procs + procs_H
    else :
        if procs[0] not in bkg_procs_from_MC :
            continue
    if specific_syst == "pdf_qg_2" :
        specific_syst_use = "pdf_qg"
    else :
        specific_syst_use = specific_syst
    cb.cp().process(procs).AddSyst(cb,  specific_syst_use, "lnN", ch.SystMap()(theory_ln_Syst[specific_syst]["value"]))
    print ("added " + specific_syst + " with value " + str(theory_ln_Syst[specific_syst]["value"]) + " to processes: ", procs)

########################################
# BR syst
for proc in higgs_procs_plain :
    if use_Exptl_HiggsBR_Uncs: BRs = higgsBR_exptl
    else :  BRs = higgsBR_theo
    for key in BRs:
        if key in proc :
            if (key=="hww" and "hwwhww" in proc) or (key=="htt" and"htthtt" in proc) or (key=="hzz" and"hzzhzz" in proc):
                continue
            if "hwwhww" in key:
                cb.cp().process([proc]).AddSyst(cb, "BR_hww", "lnN", ch.SystMap()(BRs[key]))
                print ("added " + "BR_hww (hwwhww)" + " uncertanity to process: " + proc + " of value = " + str(BRs[key]))
            elif "hzzhzz" in key:
                cb.cp().process([proc]).AddSyst(cb, "BR_hzz", "lnN", ch.SystMap()(BRs[key]))
                print ("added " + "BR_hzz (hzzhzz)" + " uncertanity to process: " + proc + " of value = " + str(BRs[key]))
            elif "htthtt" in key:
                cb.cp().process([proc]).AddSyst(cb, "BR_htt", "lnN", ch.SystMap()(BRs[key]))
                print ("added " + "BR_htt (htthtt)" + " uncertanity to process: " + proc + " of value = " + str(BRs[key]))
            else:
                cb.cp().process([proc]).AddSyst(cb, "BR_%s" % key, "lnN", ch.SystMap()(BRs[key]))
                print ("added " + "BR_%s" % key + " uncertanity to process: " + proc + " of value = " + str(BRs[key]))
    if ("ttH" in proc or "ZH" in proc or "WH" in proc) and analysis == "ttH":
        key = "hbb"
        cb.cp().process([proc]).AddSyst(cb, "BR_%s" % key, "lnN", ch.SystMap()(BRs[key]))
        print ("added " + "BR_%s" % key + " uncertanity to process: " + proc + " of value = " + str(BRs[key]))

########################################
# specifics for cards with tH-kinematics
if tH_kin and analysis == "ttH": # [k for k,v in list_channel_opt.items()
    MC_proc = [ procc.replace(coupling+"_", "") for procc in MC_proc ]
    print (coupling+"_", "MC_proc", MC_proc)
    for proc in ["TTW", "TTZ"] :
        cb.cp().process([proc]).AddSyst(cb, "CMS_ttHl_%s_lnU" % proc, "lnU", ch.SystMap()(3.0))
        print ("added", "CMS_ttHl_%s_lnU" % proc)
    from CombineHarvester.ttH_htt.data_manager import extract_thu
    for proc in ["tHq", "tHW"] :
        # https://twiki.cern.ch/twiki/pub/CMS/SingleTopHiggsGeneration13TeV/tHQ_cross_sections.txt
        # https://twiki.cern.ch/twiki/pub/CMS/SingleTopHiggsGeneration13TeV/tHW_cross_sections.txt
        thuncertainty = extract_thu(proc, coupling)
        if coupling == "kt_1_kv_1" :
            procdecays = [proc + "_htt" , proc + "_hzz", proc + "_hww"]
        else :
            procdecays = [proc + "_" + coupling + "_htt" , proc + "_" + coupling + "_hzz", proc + "_" + coupling + "_hww"]
        cb.cp().process(procdecays).AddSyst(cb, "pdf_qg", "lnN", ch.SystMap()(thuncertainty["pdf"]))
        print ("added", "pdf_qg" , thuncertainty["pdf"], procdecays)
        cb.cp().process(procdecays).AddSyst(cb, "QCDscale_qg", "lnN", ch.SystMap()((thuncertainty["qcddo"], thuncertainty["qcdup"])))
        print ("added", "QCDscale_qg", (thuncertainty["qcddo"], thuncertainty["qcdup"]), procdecays)

########################################
if shape :
    ########################################
    # MC estimated shape syst
    #for MC_shape_syst in MC_shape_systs_uncorrelated + MC_shape_systs_correlated + JES_shape_systs_Uncorrelated :
    #    if era == 2018 and MC_shape_syst == "CMS_ttHl_l1PreFire" : continue
    #    cb.cp().process(MC_proc).AddSyst(cb,  MC_shape_syst, "shape", ch.SystMap()(1.0))
    #    print ("added " + MC_shape_syst + " as shape uncertainty to the MC processes")
    ########################################
    # channel specific estimated shape syst
    specific_shape_systs = specific_syst_list["specific_shape"]
    print("specific_shape_systs", specific_syst_list['specific_shape_to_shape_systs'])
    for specific_syst in specific_shape_systs :
        if era == 2018 and specific_syst == "CMS_ttHl_l1PreFire" :
            continue
        #if "SS" in output_file and ("JER" in specific_syst or "JES" in specific_syst ) and not ( "HEM" in specific_syst )  :
        #    continue
        if ( "HEM" in specific_syst ) and era != 2018:
            print ("skkiping ", specific_syst, "as it is not era 2018")
            continue
        if "HEM" in specific_syst and stxs :
            continue
        if (specific_syst == "CMS_ttHl_Clos_e_shape") and era != 2018 and analysis == "ttH":
            continue
        if ("thu_shape_HH" in specific_syst and signal_type == "nonresLO"): # please fix
            continue
        #print specific_syst,era,channel,"111ellllf"
        if 'CMS_ttHl_FRjt_' in specific_syst and era==2016 and '0l_4tau' in channel:
            print "Do not add",specific_syst, "as era is 2016 and channel is 0l_4tau" 
            continue
        if channel not in specific_shape_systs[specific_syst]["channels"] :
            if ( "HEM" in specific_syst ) : print ("WTF", specific_shape_systs[specific_syst]["channels"])
            continue
        #if specific_shape_systs[specific_syst]["proc"] == "MCproc" :
        #    applyTo = MC_proc
        #else :
        #    applyTo = specific_shape_systs[specific_syst]["proc"]
        procs = list_proc(specific_shape_systs[specific_syst], MC_proc, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
        #if("HEM" in specific_syst and signal_type == "nonresNLO"): # fix this!!!!
        #    procs = list_proc(specific_shape_systs[specific_syst], bkg_procs_from_MC, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
        if ("HH" in specific_shape_systs[specific_syst]["proc"][0] and analysis == "HH" ):
            procs = []
            for pr in higgs_procs_plain:
                if specific_shape_systs[specific_syst]["proc"][0] in pr or ("spin" in pr and "thu_shape_HH" not in specific_syst): 
                    procs.append(pr)
        # that above take the overlap of the lists
        if len(procs) == 0 :
            continue
        # remove low yield procs
        procs_for_shape = []
        for p in procs:
            if p is "ZH_htt" and era==2018 and channel=="2l_2tau":
                continue
            if p not in bkg_procs_lowYield:
                upDoNom= [p + '_'+ specific_syst + 'Up', p + '_'+ specific_syst + 'Down',p]
                if filter_genuineShape(inputShapes, upDoNom):# or (not removeLowImpactShapes):
                    procs_for_shape.append(p)
                else: 
                    print"Do not add ",specific_syst, "for ",p, "as shape effect and yield effect are below 0.1%"
            else:
                print "Do not add ",specific_syst, "for ",p, "as its Yield is below 1%"
        if 'CMS_ttHl_trigger' in specific_syst and era==2018 and '1l_3tau' in channel:
            if 'ttH_htt' in procs_for_shape:
                print "remove", specific_syst, "from process ttH_htt inchannel 1l_3tau as it is 2018" 
                procs_for_shape.remove('ttH_htt')
            if 'ggHH_hzzhww' in procs_for_shape:
                procs_for_shape.remove('ggHH_hzzhww')
        cb.cp().process(procs_for_shape).AddSyst(cb,  specific_syst, "shape", ch.SystMap()(1.0))
        print ("added " + specific_syst + " as shape uncertainty to ", procs_for_shape)

########################################
# Specific channels lnN syst
specific_ln_systs  = specific_syst_list["specific_ln_systs"]
for specific_syst in specific_ln_systs :
    if channel not in specific_ln_systs[specific_syst]["channels"] :
        print ("Skipped ", specific_syst , " in ", channel)
        continue
    if specific_ln_systs[specific_syst]['proc'] == ['SingleHiggs']:
        specific_ln_systs[specific_syst]['proc'] = singlehiggs_procs_w_BR
    procs = list_proc(specific_ln_systs[specific_syst], MC_proc, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
    if len(procs) == 0 :
        continue
    name_syst = specific_syst 
    if specific_ln_systs[specific_syst]["renameTo"]: 
        name_syst=specific_ln_systs[specific_syst]["renameTo"]
        name_syst = name_syst.replace('ERA', str(era))
        if 'EVTCAT' in name_syst:
            name_syst = name_syst.replace('EVTCAT', subcat)
            if 'fakes_' not in name_syst:
                if 'Other' in subcat and procs[0] == 'Other_bbWW':
                    continue
                elif 'H_resolved_2b' in subcat and len(list(set(procs) - set(singlehiggs_procs_w_BR))) == 0:
                    continue
                elif 'resolved' in subcat and ((procs[0] == "WJets" and "W" in subcat) or procs[0] in subcat):
                    continue
    if "CHANNEL" in name_syst: name_syst = name_syst.replace("CHANNEL",channel)
    if not specific_ln_systs[specific_syst]["correlated"] :
        name_syst = name_syst.replace("Era",str(era))
        name_syst = name_syst.replace("%sl" % analysis, "%sl%s" % (analysis, str(era - 2000)))
        # assuming that the syst for the HH analysis with have the label HHl
    if "lnU" in name_syst :
        cb.cp().process(procs).AddSyst(cb,  name_syst, "lnU", ch.SystMap()(specific_ln_systs[specific_syst]["value"]))
    else :
        cb.cp().process(procs).AddSyst(cb,  name_syst, "lnN", ch.SystMap()(specific_ln_systs[specific_syst]["value"]))
    print ("added " + name_syst + " with value " + str(specific_ln_systs[specific_syst]["value"]) + " to processes: ",  specific_ln_systs[specific_syst]["proc"] )

########################################
finalFile = inputShapes
if list_channel_opt[channel]["isSMCSplit"] :
    print ("Construct templates for fake/gentau systematics:")
    specific_ln_shape_systs    = specific_syst_list["specific_ln_to_shape_systs"]
    specific_shape_shape_systs = specific_syst_list["specific_shape_to_shape_systs"]
    finalFile = construct_templates(cb, ch, specific_ln_shape_systs, specific_shape_shape_systs, inputShapes , MC_proc, shape, noX_prefix )

########################################
# bin by bin stat syst
if not binByBin:
    cb.cp().SetAutoMCStats(cb, 10)
  
if noX_prefix :
    cb.cp().backgrounds().ExtractShapes(
        finalFile,
        "$PROCESS",
        "$PROCESS_$SYSTEMATIC")
    cb.cp().signals().ExtractShapes(
        finalFile,
        "$PROCESS",
        "$PROCESS_$SYSTEMATIC")
else :
    cb.cp().backgrounds().ExtractShapes(
        finalFile,
        "x_$PROCESS",
        "x_$PROCESS_$SYSTEMATIC")
    cb.cp().signals().ExtractShapes(
        finalFile,
        "x_$PROCESS",
        "x_$PROCESS_$SYSTEMATIC")
########################################
# rename some shape systematics according to era to keep them uncorrelated
if shape :
    ########################################
    if list_channel_opt[channel]["isSMCSplit"] :
        MC_proc_less = list(set(list(MC_proc)) - set(["Convs"]))
        for shape_syst in specific_syst_list["created_shape_to_shape_syst"] :
            MC_shape_syst = shape_syst.replace("CMS_constructed_", "CMS_")
            cb.cp().process(MC_proc_less).RenameSystematic(cb, shape_syst, MC_shape_syst)
            print ("renamed " + shape_syst + " to " +  MC_shape_syst + " to the MC processes ")
            if "tauES" in shape_syst :
                MC_shape_syst_era_3 = "CMS_scale_t_Era".replace("Era", str(era))
                cb.cp().process(MC_proc_less).RenameSystematic(cb, MC_shape_syst, MC_shape_syst_era_3)
                print ("renamed " + MC_shape_syst + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era_3)
            elif "tauID" in shape_syst :
                MC_shape_syst_era_3 = "CMS_eff_t_Era".replace("Era", str(era))
                cb.cp().process(MC_proc_less).RenameSystematic(cb, MC_shape_syst, MC_shape_syst_era_3)
                print ("renamed " + MC_shape_syst + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era_3)
            else :
                MC_shape_syst_era_2 = MC_shape_syst.replace("CMS_ttHl", "CMS_ttHl%s" % str(era).replace("20","")).replace("Era", str(era))
                cb.cp().process(MC_proc_less).RenameSystematic(cb, MC_shape_syst, MC_shape_syst_era_2)
                print ("renamed " + MC_shape_syst + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era_2)
    ##################################
    for specific_syst in specific_shape_systs :
        if channel not in specific_shape_systs[specific_syst]["channels"] :
            continue
        if era == 2018 and specific_syst == "CMS_ttHl_l1PreFire" :
            continue
        #if "SS" in output_file and ("JER" in specific_syst or "JES" in specific_syst ) :
        #    continue
        if ( "HEM" in specific_syst ) and era != 2018 :
            print ("skkiping ", specific_syst, "as it is not era 2018")
            continue
        if "HEM" in specific_syst and stxs :
            continue
        if specific_shape_systs[specific_syst]["correlated"] and specific_shape_systs[specific_syst]["renameTo"] == None :
            continue
        if ("thu_shape_HH" in specific_syst and signal_type == "nonresLO"): # please fix
            continue
        if 'CMS_ttHl_FRjt_' in specific_syst and era==2016 and '0l_4tau' in channel:
            continue
        #################
        procs = list_proc(specific_shape_systs[specific_syst], MC_proc, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
        ##if("HEM" in specific_syst and signal_type == "nonresNLO"): # fix this!!!!
        #    procs = list_proc(specific_shape_systs[specific_syst], bkg_procs_from_MC, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
        if ("HH" in specific_shape_systs[specific_syst]["proc"][0] and analysis == "HH"):
            procs = []
            for pr in higgs_procs_plain:
                if specific_shape_systs[specific_syst]["proc"][0] in pr or ("spin" in pr and "thu_shape_HH" not in specific_syst): 
                    procs.append(pr)
        # that above take the overlap of the lists
        if len(procs) == 0 :
            continue
        # remove low yield procs
        procs_for_shape = []
        for p in procs:
            if p is "ZH_htt" and era==2018 and channel=="2l_2tau":
                continue
            if p not in bkg_procs_lowYield:
                upDoNom= [p + '_'+ specific_syst + 'Up', p + '_'+ specific_syst + 'Down',p]
                if filter_genuineShape(inputShapes, upDoNom):# or (not removeLowImpactShapes):
                    procs_for_shape.append(p)
        if 'CMS_ttHl_trigger' in specific_syst and era==2018 and '1l_3tau' in channel:
            if 'ttH_htt' in procs_for_shape:
                print "remove", specific_syst, "from process ttH_htt inchannel 1l_3tau as it is 2018" 
                procs_for_shape.remove('ttH_htt')
            if 'ggHH_hzzhww' in procs_for_shape:
                procs_for_shape.remove('ggHH_hzzhww')
        #################
        if not specific_shape_systs[specific_syst]["renameTo"] == None :
            MC_shape_syst_era = specific_shape_systs[specific_syst]["renameTo"]
            #if 'EVTCAT' in MC_shape_syst_era:
             #   MC_shape_syst_era = MC_shape_syst_era.replace('EVTCAT', subcat)
            cb.cp().process(procs_for_shape).RenameSystematic(cb, specific_syst, MC_shape_syst_era)
            print ("renamed " + specific_syst + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era)
        else :
            MC_shape_syst_era = specific_syst
        if not specific_shape_systs[specific_syst]["correlated"] :
            if 'ttH' in analysis:
                MC_shape_syst_era_2 = MC_shape_syst_era.replace("CMS_ttHl", "CMS_ttHl%s" % str(era).replace("20","")).replace("Era", str(era))
            else:
                MC_shape_syst_era_2 = MC_shape_syst_era.replace("Era", str(era))
                if 'Clos' in MC_shape_syst_era_2 and analysis == "HH" and channel not in ["1l_0tau", '2l_0tau']:
                    MC_shape_syst_era_2 = MC_shape_syst_era_2+ "_" + channel
                if 'CMS_btag' in MC_shape_syst_era_2:
                    if not ('stats' in MC_shape_syst_era_2 or 'cferr' in MC_shape_syst_era_2):                        
                        if '2017' in str(era): MC_shape_syst_era_2 = MC_shape_syst_era_2.replace('2017','2017_2018')
                        if '2018' in str(era): MC_shape_syst_era_2 = MC_shape_syst_era_2.replace('2018','2017_2018')
            cb.cp().process(procs_for_shape).RenameSystematic(cb, MC_shape_syst_era, MC_shape_syst_era_2)
            print ("renamed " + MC_shape_syst_era + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era_2)
        else :
            MC_shape_syst_era_2 = MC_shape_syst_era
        ###################
        if specific_syst == "CMS_ttHl_trigger" :
            if channel in ["1l_2tau", "1l_1tau"] :
                MC_shape_syst_era_3 = MC_shape_syst_era_2 + "_leptau"
            elif channel in ["0l_2tau"] :
                MC_shape_syst_era_3 = MC_shape_syst_era_2 + "_tau"
            else :
                MC_shape_syst_era_3 = MC_shape_syst_era_2 + "_" + channel
            cb.cp().process(procs_for_shape).RenameSystematic(cb, MC_shape_syst_era_2, MC_shape_syst_era_3)
            print ("renamed " + MC_shape_syst_era_2 + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era_3)
        if  "Clos_t_norm" in specific_syst or  "Clos_t_shape" in specific_syst:
            MC_shape_syst_era_3 = MC_shape_syst_era_2 + "_" + channel
            cb.cp().process(procs_for_shape).RenameSystematic(cb, MC_shape_syst_era_2, MC_shape_syst_era_3)
            print ("renamed " + MC_shape_syst_era_2 + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era_3)

########################################
if ( not ( signal_type == "none" and mass == "none" and HHtype == "none" )) and options.output_file=="none" :
    output_file =  "%s_%s_%s_%s" % (output_file, HHtype, signal_type, mass )

if binByBin:
    bbb = ch.BinByBinFactory()
    bbb.SetAddThreshold(0.1).SetFixNorm(False)
    #bbb.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(True)
    #bbb.MergeBinErrors(cb.cp().backgrounds())
    bbb.AddBinByBin(cb.cp().backgrounds(),cb)
    sysnames = cb.syst_name_set()
    for sysname in sysnames:
        if "CMS___" in sysname:
            binname = sysname[sysname.find("bin"):]
            process = sysname[sysname.find("13TeV_")+6:sysname.find("bin")-1]
            newname="CMS_multilepton_mcStat_%s_%s_%s_%s"%(channel,era,process,binname)
            cb.cp().process([process]).RenameSystematic(cb, sysname, newname)
bins = cb.bin_set()
for b in bins :
    print ("\n Output file: " + output_file + ".txt", b )
    cb.cp().bin([b]).mass(["*"]).WriteDatacard(output_file + ".txt" , output_file + ".root")

if no_data :
    print("Making data_obs as the asimov in SM if asked to do so")
    manipulate_cards(output_file, "none", bins, no_data, bkg_procs_from_MC+higgs_procs_plain+bkg_proc_from_data, inputShapes)

if not (coupling == "none" or coupling == "kt_1_kv_1") :
    print("Renaming tH processes (remove the coupling mention to combime)")
    manipulate_cards(output_file, coupling, bins, no_data, bkg_procs_from_MC+higgs_procs_plain+bkg_proc_from_data, inputShapes)

sys.stdout.flush()
