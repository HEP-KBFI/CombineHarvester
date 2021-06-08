#!/usr/bin/env python
import os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
from io import open
exec(open(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager.py").read())

#output_cards = "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_unblinded/"
output_cards = "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_unblinded_stxs/"

eras_to_do = [ "2018", "2016", "2017" ]
make_cards = True
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--stxs",           action="store_true", dest="stxs",        help="Cards for stxs", default=False)
parser.add_option("--blinded",        action="store_true", dest="blinded",     help="Cards for stxs", default=False)
(options, args) = parser.parse_args()

make_stxs     = options.stxs
blinded       = options.blinded

# the paths aree given as 2018, it is assumed that to get the other eras just changing 2018 to eg 2017
cards_fullSyst_june22 = {
    ## /home/karl/ttHAnalysis/2018/2020Jun18/datacards -- 7 tau channels;
    ## updating ttW to NLO
    ############################
    "2lss_1tau_rest"         : {"channel" : "2lss_1tau_rest", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/2lss_1tau/addSystFakeRates/addSystFakeRates_2lss_1tau_sumOS_output_NN_rest.root"},
    "2lss_1tau_tH"           : {"channel" : "2lss_1tau_tH",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/2lss_1tau/addSystFakeRates/addSystFakeRates_2lss_1tau_sumOS_output_NN_tH.root"},
    "2lss_1tau_ttH"          : {"channel" : "2lss_1tau_ttH",  "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/2lss_1tau/addSystFakeRates/addSystFakeRates_2lss_1tau_sumOS_output_NN_ttH.root"},
    #############################
    "0l_2tau"                : {"channel" : "0l_2tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/0l_2tau/addSystFakeRates/addSystFakeRates_0l_2tau_0l_2tau_mvaOutput_Legacy_OS.root"},
    "1l_2tau"                : {"channel" : "1l_2tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/1l_2tau/addSystFakeRates/addSystFakeRates_1l_2tau_mvaOutput_legacy_OS.root"},
    "1l_1tau"                : {"channel" : "1l_1tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/1l_1tau/addSystFakeRates/addSystFakeRates_1l_1tau_1l_1tau_mvaOutput_Legacy_6_disabled.root"},
    "2los_1tau"              : {"channel" : "2los_1tau", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/2los_1tau/addSystFakeRates/addSystFakeRates_2los_1tau_mvaOutput_legacy.root"},
    ##############################
    "2l_2tau"                : {"channel" : "2l_2tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/2l_2tau/addSystFakeRates/addSystFakeRates_2l_2tau_lepdisabled_taudisabled_sumOS_mvaOutput_final.root"},
    "3l_1tau"                : {"channel" : "3l_1tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards/2018/datacards/3l_1tau/addSystFakeRates/addSystFakeRates_3l_1tau_OS_mvaOutput_legacy.root"}, #
    }

cards_fullSyst_june22_stxs = {
    ## /home/karl/archive/201*/2020Jun18/datacards/
    ############################
    "2lss_1tau_rest"         : {"channel" : "2lss_1tau_rest", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/2lss_1tau/stxs/stxs_2lss_1tau_sumOS_output_NN_rest.root"},
    "2lss_1tau_tH"           : {"channel" : "2lss_1tau_tH",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/2lss_1tau/stxs/stxs_2lss_1tau_sumOS_output_NN_tH.root"},
    "2lss_1tau_ttH"          : {"channel" : "2lss_1tau_ttH",  "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/2lss_1tau/stxs/stxs_2lss_1tau_sumOS_output_NN_ttH.root"},
    #############################
    "0l_2tau"                : {"channel" : "0l_2tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/0l_2tau/stxs/stxs_0l_2tau_0l_2tau_mvaOutput_Legacy_OS.root"},
    "1l_2tau"                : {"channel" : "1l_2tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/1l_2tau/stxs/stxs_1l_2tau_mvaOutput_legacy_OS.root"},
    "1l_1tau"                : {"channel" : "1l_1tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/1l_1tau/stxs/stxs_1l_1tau_1l_1tau_mvaOutput_Legacy_6_disabled.root"},
    "2los_1tau"              : {"channel" : "2los_1tau", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/2los_1tau/stxs/stxs_2los_1tau_mvaOutput_legacy.root"},
    ##############################
    "2l_2tau"                : {"channel" : "2l_2tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/2l_2tau/stxs/stxs_2l_2tau_lepdisabled_taudisabled_sumOS_mvaOutput_final.root"},
    "3l_1tau"                : {"channel" : "3l_1tau",   "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_22June20_prepareDatacards_stxs/2018/datacards/3l_1tau/stxs/stxs_3l_1tau_OS_mvaOutput_legacy.root"}, #
    }

cards_CR_fullSyst_march21 = {
    ## - /home/karl/ttHAnalysis/$ERA/2020Mar18SB -- 1l+2tauSS SB (no regrouped JES or split JER, though);
    "1l_2tau_SS"            : {"channel" : "1l_2tau", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_21March20_prepareDatacards/2018/1l_2tau_SS/addSystFakeRates/addSystFakeRates_1l_2tau_mvaOutput_legacy_SS.root"},
    "1l_2tau_SS_mTTVis"     : {"channel" : "1l_2tau", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_21March20_prepareDatacards/2018/1l_2tau_SS/addSystFakeRates/addSystFakeRates_1l_2tau_mTauTauVis_SS.root"},
    "1l_2tau_SS_numJets"    : {"channel" : "1l_2tau", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_21March20_prepareDatacards/2018/1l_2tau_SS/addSystFakeRates/addSystFakeRates_1l_2tau_numJets_SS.root"},
    "1l_2tau_SS_HTT"        : {"channel" : "1l_2tau", "shapes"   : "/home/acaan/CMSSW_10_2_13/src/cards_set/legacy_TLL_21March20_prepareDatacards/2018/1l_2tau_SS/addSystFakeRates/addSystFakeRates_1l_2tau_HTT_SS.root"}
}

cards_SVA = {
    #"2lss_0tau_cr"        : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_cr.root"},
    #"2lss_0tau_ee_hj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_hj_neg.root"},
    #"2lss_0tau_ee_hj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_hj_pos.root"},
    #"2lss_0tau_ee_lj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_lj_neg.root"},
    #"2lss_0tau_ee_lj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_lj_pos.root"},
    #"2lss_0tau_em_hj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_hj_neg.root"},
    #"2lss_0tau_em_hj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_hj_pos.root"},
    #"2lss_0tau_em_lj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_lj_neg.root"},
    #"2lss_0tau_em_lj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_lj_pos.root"},
    #"2lss_0tau_mm_hj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_hj_neg.root"},
    #"2lss_0tau_mm_hj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_hj_pos.root"},
    #"2lss_0tau_mm_lj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_lj_neg.root"},
    #"2lss_0tau_mm_lj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_2lss_0tau_16Jan20_2018/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_lj_pos.root"},
    ######################
    ## 3l
    #"3l_0tau_hj_neg"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_0tau_16Jan20_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_mass_3L_hj_neg.root"},
    #"3l_0tau_hj_pos"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_0tau_16Jan20_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_mass_3L_hj_pos.root"},
    #"3l_0tau_lj_neg"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_0tau_16Jan20_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_mass_3L_lj_neg.root"},
    #"3l_0tau_lj_pos"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_0tau_16Jan20_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_mass_3L_lj_pos.root"},
    ###########################
    "2lss_1tau"              : {"channel" : "2lss_1tau", "shapes" : "/home/acaan/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/2lss_1tau_addSystFakeRates_SVA/2018/addSystFakeRates_2lss_1tau_sumOS_mTauTauVis1.root"},
    ###########################
    #"3l_cr_eee"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_cR_16Jan20_2018//datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_eee.root"},
    #"3l_cr_eem"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_cR_16Jan20_2018//datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_eem.root"},
    #"3l_cr_emm"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_cR_16Jan20_2018//datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_emm.root"},
    #"3l_cr_mmm"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_3l_cR_16Jan20_2018//datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_mmm.root"},
    ###########################
    #"4l_cr"                 : {"channel" : "4lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_4l_cR_16Jan20_2018/datacards/4lctrl/prepareDatacards/prepareDatacards_4lctrl_OS_control.root"},

}
cards_to_do = cards_fullSyst_june22
if make_stxs :
    cards_to_do = cards_fullSyst_june22_stxs

for era in eras_to_do :
    if make_cards :
        for key in cards_to_do :
            print (key)
            print (cards_to_do[key])
            cmd = "WriteDatacards.py "
            cmd += "--inputShapes %s " % (cards_to_do[key]["shapes"].replace("2018", era))
            cmd += "--channel %s "     % (cards_to_do[key]["channel"].replace("2018", era))
            cmd += "--cardFolder %s "  % output_cards
            cmd += "--noX_prefix  "
            if make_stxs :
                cmd += " --stxs --forceModifyShapes "
            #if not "ctrl" in cards_to_do[key]["channel"]  :
            #    cmd += "--no_data "
            cmd += "--era %s" % str(era)
            cmd += " --output_file %s/ttH_%s_%s" % (output_cards, key, era)
            cmd += " --shapeSyst "
            runCombineCmd(cmd, '.', "%s/ttH_%s_%s.log" % (output_cards, key, era))
            print ("output card/log saved on: %s/ttH_%s_%s.txt/root/log" % (output_cards, key, era))
    #######################
    print ( "combine cards to make plots -- the order of lists of flavours is important" )
    if "3l_cr_eee" in list(cards_to_do.keys()) :
        cmd = "combineCards.py "
        for flavor in ["eee", "eem", "emm", "mmm"] :
            cmd += " ttH_3lctr_%s=ttH_3l_cr_%s_%s.txt" % (flavor, flavor, era)
        cmd += " > combo_ttH_3l_cr_%s.txt" % era
        runCombineCmd(cmd, output_cards)
    #
    if "2lss_0tau_ee_Restnode" in list(cards_to_do.keys()) :
        for node in ["Rest", "ttH", "ttW", "tHQ"] :
          cmd = "combineCards.py "
          for flavor in ["ee", "em", "mm"] :
            cmd += " ttH_2lss_0tau_%s_%snode=ttH_2lss_0tau_%s_%snode_%s.txt" % (flavor, node, flavor, node, era)
          cmd += " > combo_ttH_2lss_0tau_%snode_%s.txt" % (node, era)
          runCombineCmd(cmd, output_cards)
    #
    if "2lss_0tau_ee_hj_neg" in list(cards_to_do.keys()) :
      for type in ["pos", "neg"] :
        for node in ["hj", "lj"] :
          cmd = "combineCards.py "
          for flavor in ["ee", "em", "mm"] :
            cmd += " ttH_2lss_0tau_%s_%s_%s=ttH_2lss_0tau_%s_%s_%s_%s.txt" % (flavor, node, type, flavor, node, type, era)
          cmd += " > combo_ttH_2lss_0tau_%s_%s_%s.txt" % (node, type, era)
          runCombineCmd(cmd, output_cards)
    #
    if "3l_0tau_rest_eee" in list(cards_to_do.keys()) :
        for node in ["ttH", "tH"] :
          cmd = "combineCards.py "
          for flavor in ["bt", "bl"] :
            cmd += " ttH_3l_0tau_%s_%s=ttH_3l_0tau_%s_%s_%s.txt" % (node, flavor, node, flavor, era)
          cmd += " > combo_ttH_3l_0tau_%s_%s.txt" % (node, era)
          runCombineCmd(cmd, output_cards)
        cmd = "combineCards.py "
        for flavor in ["eee", "eem", "emm", "mmm"] :
            cmd += " ttH_3l_0tau_rest_%s=ttH_3l_0tau_rest_%s_%s.txt" % (flavor, flavor, era)
        cmd += " > combo_ttH_3l_0tau_rest_%s.txt" % (era)
        runCombineCmd(cmd, output_cards)
    #
    if "2lss_1tau_rest" in list(cards_to_do.keys()) :
        cmd = "combineCards.py "
        for node in ["ttH", "tH", "rest"] :
            cmd += "ttH_2lss_1tau_%s=ttH_2lss_0tau_%s_%s.txt" % (node, node, era)
        cmd += " > combo_ttH_2lss_1tau_%s.txt" % (era)
        runCombineCmd(cmd, output_cards)
