#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import ROOT
import sys, os, re, shlex
from subprocess import Popen, PIPE
from CombineHarvester.ttH_htt.data_manager import rename_tH, lists_overlap, construct_templates, list_proc, make_threshold
sys.stdout.flush()

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputShapes",    type="string",       dest="inputShapes", help="Full path of prepareDatacards.root")
parser.add_option("--channel",        type="string",       dest="channel",     help="Channel to assume (to get the correct set of syst)")
parser.add_option("--cardFolder",     type="string",       dest="cardFolder",  help="Folder where to save the datacards (relative or full).\n Default: teste_datacards",  default="teste_datacards")
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

(options, args) = parser.parse_args()

inputShapes = options.inputShapes
channel     = options.channel
era         = options.era
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
tH_kin       = options.tH_kin
use_Exptl_HiggsBR_Uncs = options.use_Exptl_HiggsBR_Uncs
if use_Exptl_HiggsBR_Uncs:
    print("Using Experimental Unc.s on Higgs BRs")
else:
    print("Using Theoretical Unc.s on Higgs BRs")

if not os.path.exists(cardFolder):
    os.makedirs(cardFolder)

syst_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_syst.py"
execfile(syst_file)
print ("syst values and channels options taken from: " +  syst_file)

info_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_channels.py"
execfile(info_file)
print ("list of signals/bkgs by channel taken from: " +  info_file)

higgs_procs = list_channels(analysis, fake_mc)["higgs_procs"]
list_channel_opt   = list_channels(analysis, fake_mc)["info_bkg_channel"]
bkg_proc_from_data = list_channel_opt[channel]["bkg_proc_from_data"]
bkg_procs_from_MC  = list_channel_opt[channel]["bkg_procs_from_MC"]

# if a coupling is done read the tH signal with that coupling on naming convention
if not (coupling == "none" or coupling == "kt_1_kv_1") :
    higgs_procs = [ [ entry.replace("tHq_", "tHq_%s_" % coupling).replace("tHW_", "tHW_%s_" % coupling) for entry in entries ] for entries in higgs_procs ]

higgs_procs_plain = sum(higgs_procs,[])

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
    #higgs_procs        = [ entries for entries in bkg_procs_from_MC if "TTW" in entry or "TTZ" in entry ]
    print ("BKG from MC   (new): ", bkg_procs_from_MC)
    print ("signal        (new): ", ["TTW", "TTZ"])
    higgs_procs_plain = ["TTW", "TTZ"] #higgs_procs


# check a threshold on processes
print ("do not add a process to datacard if the yield is smaller than 0.01")
bkg_proc_from_data = make_threshold(0.01, bkg_proc_from_data,  inputShapes)
bkg_procs_from_MC  = make_threshold(0.01, bkg_procs_from_MC, inputShapes)
higgs_procs_plain  = make_threshold(0.01, higgs_procs_plain, inputShapes)

print ("final list of signal/bkg to add to datacards")
MC_proc = higgs_procs_plain + bkg_procs_from_MC
print ("MC processes:")
print ("BKG from MC  (original)  : ", bkg_procs_from_MC)
print ("BKG from data (original) : ", bkg_proc_from_data)
print ("signal        (original): ", higgs_procs_plain)

specific_syst_list = specific_syst(analysis, list_channel_opt)
print("analysis type        :", analysis)

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
cb.cp().signals().AddSyst(cb, "lumi_%s" % str(era), "lnN", ch.SystMap()(lumiSyst[era]))

#######################################
# FIXME: one of the syst is logUniform -- fix
if 0 > 1 : # FIXME: remind why we added that at some point
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
# add theory systematics
for specific_syst in theory_ln_Syst :
    procs = theory_ln_Syst[specific_syst]["proc"]
    if len(procs) == 0 :
        continue
    if "HH" in procs[0] :
        for decay in list_channels(analysis, fake_mc)["decays_hh"] :
            procs = procs + [procs[0] + decay]
    elif "H" in procs[0] :
        if tH_kin and ("tHq" in procs[0] or "tHW" in procs[0]) :
            continue
        for decay in list_channels(analysis, fake_mc)["decays"] :
            procs = procs + [procs[0] + decay]
    else :
        if procs[0] not in bkg_procs_from_MC :
            continue
    cb.cp().process(procs).AddSyst(cb,  specific_syst, "lnN", ch.SystMap()(theory_ln_Syst[specific_syst]["value"]))
    print ("added " + specific_syst + " with value " + str(theory_ln_Syst[specific_syst]["value"]) + " to processes: ", procs)

########################################
# BR syst
for proc in higgs_procs_plain :
    if use_Exptl_HiggsBR_Uncs: BRs = higgsBR_exptl
    else :  BRs = higgsBR_theo
    for key in BRs:
        if key in proc :
            cb.cp().process([proc]).AddSyst(cb, "BR_%s" % key, "lnN", ch.SystMap()(higgsBR_exptl[key]))
            print ("added " + "BR_%s" % key + " uncertanity to process: " + proc + " of value = " + str(higgsBR_exptl[key]))

########################################
# specifics for cards with tH-kinematics
if tH_kin :
    MC_proc = [ proc.replace(coupling, "") for proc in MC_proc ]
    for proc in ["TTW", "TTZ"] :
        cb.cp().process([proc]).AddSyst(cb, "CMS_ttHl_%s_lnU" % proc, "lnU", ch.SystMap()(2.0))
        print ("added", "CMS_ttHl_%s_lnU" % proc)
    from CombineHarvester.ttH_htt.data_manager import extract_thu
    for proc in ["tHq", "tHW"] :
        # https://twiki.cern.ch/twiki/pub/CMS/SingleTopHiggsGeneration13TeV/tHQ_cross_sections.txt
        # https://twiki.cern.ch/twiki/pub/CMS/SingleTopHiggsGeneration13TeV/tHW_cross_sections.txt
        thuncertainty = extract_thu(proc, coupling)
        procdecays = [proc + "_" + coupling + "_htt" , proc + "_" + coupling + "_hzz", proc + "_" + coupling + "_hww"]
        cb.cp().process(procdecays).AddSyst(cb, "pdf_%s" % proc, "lnU", ch.SystMap()(thuncertainty["pdf"]))
        print ("added", "pdf_%s" % proc, thuncertainty["pdf"])
        cb.cp().process(procdecays).AddSyst(cb, "QCDscale_%s" % proc, "lnU", ch.SystMap()((thuncertainty["qcddo"], thuncertainty["qcdup"])))
        print ("added", "QCDscale_%s" % proc, (thuncertainty["qcddo"], thuncertainty["qcdup"]))

########################################
if shape :
    ########################################
    # fakes shape syst -- all uncorrelated
    for fake_shape_syst in fake_shape_systs_uncorrelated :
        cb.cp().process(["fakes_data"]).AddSyst(cb,  fake_shape_syst, "shape", ch.SystMap()(1.0))
        print ("added " + fake_shape_syst + " as shape uncertainty to " + "fakes_data")
    ########################################
    # MC estimated shape syst
    for MC_shape_syst in MC_shape_systs_uncorrelated + MC_shape_systs_correlated + JES_shape_systs_Uncorrelated :
        cb.cp().process(MC_proc).AddSyst(cb,  MC_shape_syst, "shape", ch.SystMap()(1.0))
        print ("added " + MC_shape_syst + " as shape uncertainty to the MC processes")
    ########################################
    # channel specific estimated shape syst
    #print("specific_shape", specific_shape)
    specific_shape_systs = specific_syst_list["specific_shape"]
    print("specific_shape_systs", specific_syst_list['specific_shape_to_shape_systs'])
    for specific_syst in specific_shape_systs :
        if channel not in specific_shape_systs[specific_syst]["channels"] :
            continue
        procs = list_proc(specific_shape_systs[specific_syst], MC_proc, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
        if len(procs) == 0 :
            continue
        cb.cp().process(procs).AddSyst(cb,  specific_syst, "shape", ch.SystMap()(1.0))
        print ("added " + specific_syst + " as shape uncertainty to ", procs)

########################################
# Specific channels lnN syst
specific_ln_systs  = specific_syst_list["specific_ln_systs"]

for specific_syst in specific_ln_systs :
    if channel not in specific_ln_systs[specific_syst]["channels"] :
        continue
    procs = list_proc(specific_ln_systs[specific_syst], MC_proc, bkg_proc_from_data + bkg_procs_from_MC, specific_syst)
    if len(procs) == 0 :
        continue
    name_syst = specific_syst
    if not specific_ln_systs[specific_syst]["correlated"] :
        name_syst = specific_syst.replace("%sl" % analysis, "%sl%s" % (analysis, str(era - 2000)))
        # assuming that the syst for the HH analysis with have the label HHl
    if "lnU" in name_syst :
        cb.cp().process(procs).AddSyst(cb,  name_syst, "lnU", ch.SystMap()(specific_ln_systs[specific_syst]["value"]))
    else :
        cb.cp().process(procs).AddSyst(cb,  name_syst, "lnN", ch.SystMap()(specific_ln_systs[specific_syst]["value"]))
    print ("added " + name_syst + " with value " + str(specific_ln_systs[specific_syst]["value"]) + " to processes: ",  specific_ln_systs[specific_syst]["proc"] )

########################################
# Construct templates for fake/gentau syst if relevant
finalFile = inputShapes
if list_channel_opt[channel]["isSMCSplit"] :
    specific_ln_shape_systs    = specific_syst_list["specific_ln_to_shape_systs"]
    specific_shape_shape_systs = specific_syst_list["specific_shape_to_shape_systs"]
    finalFile = construct_templates(cb, ch, specific_ln_shape_systs, specific_shape_shape_systs, inputShapes , MC_proc, shape, noX_prefix )

########################################
# bin by bin stat syst
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
    # fakes shape syst
    for fake_shape_syst in fake_shape_systs_uncorrelated :
        fake_shape_syst_era = fake_shape_syst.replace("CMS_ttHl", "CMS_ttHl%s" % (str(era-2000)))
        cb.cp().process(["fakes_data"]).RenameSystematic(cb, fake_shape_syst, fake_shape_syst_era)
        print ("renamed " + fake_shape_syst + " to " + "fakes_data" + " as: " + fake_shape_syst_era)
    ########################################
    # MC estimated shape syst
    for MC_shape_syst in MC_shape_systs_uncorrelated :
        MC_shape_syst_era = MC_shape_syst.replace("CMS_ttHl", "CMS_ttHl%s" % str(era).replace("20",""))
        cb.cp().process(MC_proc).RenameSystematic(cb, MC_shape_syst, MC_shape_syst_era)
        print ("renamed " + MC_shape_syst + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era)
    for MC_shape_syst in JES_shape_systs_Uncorrelated :
        MC_shape_syst_era = MC_shape_syst.replace("_Era", str(era))
        cb.cp().process(MC_proc).RenameSystematic(cb, MC_shape_syst, MC_shape_syst_era)
        print ("renamed " + MC_shape_syst + " as shape uncertainty to MC prcesses to " + MC_shape_syst_era)

    cb.cp().process(MC_proc).RenameSystematic(cb, "CMS_ttHl_JES",   "CMS_scale_j")
    print ("renamed CMS_ttHl_JES to CMS_scale_j to the MC processes ")

    cb.cp().process(MC_proc).RenameSystematic(cb, "CMS_ttHl_tauES", "CMS_scale_t")
    print ("renamed CMS_ttHl_tauES to CMS_scale_t to the MC processes ")

    #for shape_syst in created_shape_to_shape_syst :
    #    cb.cp().process(MC_proc).RenameSystematic(cb, shape_syst, shape_syst.replace("CMS_constructed_", "CMS_"))
    #    print ("renamed " + shape_syst + " to " +  shape_syst.replace("CMS_constructed_", "CMS_") + " to the MC processes ")
    # Xanda: FIXME for isMCsplit


### reminiscent of doing cards with wrong XS normalization, leave it here in case we need again
def scaleBy(proc):
    # scale tHq by 3 and WZ by 2
    if "tHq" in proc.process() :
        proc.set_rate(proc.rate()*3)
        print ("scale " +   str(proc.process()) +  " by " + str(3))
    #if "WZ"  in proc.process() :
    #     proc.set_rate(proc.rate()*2)
    #     print ("scale " +   str(proc.process()) +  " by " + str(2))
    #    p.set_signal(True)

#print ("placeholder for 2lss 1tau processes ")
#cb.ForEachProc(scaleBy)

########################################
# output the card
if options.output_file == "none" :
    output_file = cardFolder + "/" + str(os.path.basename(inputShapes)).replace(".root","").replace("prepareDatacards", "datacard")
else :
    output_file = options.output_file

if not (coupling == "none") :
    output_file += "_" + coupling

bins = cb.bin_set()
for b in bins :
    print ("\n Output file: " + output_file + ".txt")
    cb.cp().bin([b]).mass(["*"]).WriteDatacard(output_file + ".txt" , output_file + ".root")

rename_tH(output_file, "none", bins, no_data, bkg_procs_from_MC+higgs_procs_plain+bkg_proc_from_data)
if not (coupling == "none" or coupling == "kt_1_kv_1") :
    print("Renaming tH processes (remove the coupling mention to combime)")
    rename_tH(output_file, coupling, bins, no_data, bkg_procs_from_MC+higgs_procs_plain+bkg_proc_from_data)

sys.stdout.flush()
