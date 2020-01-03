#!/usr/bin/env python
import os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
from io import open
exec(open(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager.py").read())

output_cards = "/home/acaan/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/TLL_legacy_MVAs/"
eras_to_do = ["2018", ] # , "2016" "2017"
make_cards = True

cards_MVA = {
    ### there is only 2018 while we cannot check with Oviedo
    #"2lss_0tau_ee_Restnode" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_rest_ee.root"},
    #"2lss_0tau_em_Restnode" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_rest_em.root"},
    #"2lss_0tau_mm_Restnode" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_rest_mm.root"} ,
    #"2lss_0tau_ee_tHQnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_tH_ee.root"},
    #"2lss_0tau_em_tHQnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_tH_em.root"},
    #"2lss_0tau_mm_tHQnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_tH_mm.root"},
    #"2lss_0tau_ee_ttHnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_ttH_ee.root"},
    #"2lss_0tau_em_ttHnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_ttH_em.root"},
    #"2lss_0tau_mm_ttHnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_ttH_mm.root"},
    #"2lss_0tau_ee_ttWnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_ttW_ee.root"},
    #"2lss_0tau_em_ttWnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_ttW_em.root"},
    #"2lss_0tau_mm_ttWnode"  : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_output_NN_ttW_mm.root"},
    ########################
    "3l_0tau_rest_eee"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_rest_eee.root"},
    "3l_0tau_rest_eem"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_rest_eem.root"},
    "3l_0tau_rest_emm"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_rest_emm.root"},
    "3l_0tau_rest_mmm"      : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_rest_mmm.root"},
    "3l_0tau_tH_bl"         : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_tH_bl.root"},
    "3l_0tau_tH_bt"         : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_tH_bt.root"},
    "3l_0tau_ttH_bl"        : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_ttH_bl.root"},
    "3l_0tau_ttH_bt"        : {"channel" : "3l_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_2018/datacards/3l/prepareDatacards/prepareDatacards_3l_OS_output_NN_ttH_bt.root"},
    ###########################
    "2lss_1tau_rest"        : {"channel" : "2lss_1tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_2lss_1tau_2018/datacards/2lss_1tau/prepareDatacards/prepareDatacards_2lss_1tau_sumOS_output_NN_rest.root"}, # mT_lep is from lep_pt
    "2lss_1tau_tH"          : {"channel" : "2lss_1tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_2lss_1tau_2018/datacards/2lss_1tau/prepareDatacards/prepareDatacards_2lss_1tau_sumOS_output_NN_tH.root"},   # mT_lep is from lep_pt
    "2lss_1tau_ttH"         : {"channel" : "2lss_1tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_2lss_1tau_2018/datacards/2lss_1tau/prepareDatacards/prepareDatacards_2lss_1tau_sumOS_output_NN_ttH.root"},  # mT_lep is from lep_pt
    #############################
    "0l_2tau"                : {"channel" : "0l_2tau", "shapes" : "/home/arun/ttHAnalysis/2018/2019Dec23/datacards/0l_2tau/prepareDatacards/prepareDatacards_0l_2tau_0l_2tau_mvaOutput_Legacy.root"},            # mT_lep is from lep_pt
    "1l_2tau"                : {"channel" : "1l_2tau", "shapes" : "/home/arun/ttHAnalysis/2018/2019Dec23/datacards/1l_2tau/prepareDatacards/prepareDatacards_1l_2tau_mvaOutput_legacy.root"},                    # mT_lep is from lep_pt ## needs to have less bins
    "1l_1tau"                : {"channel" : "1l_1tau", "shapes" : "/home/arun/ttHAnalysis/2018/2019Dec23/datacards/1l_1tau/prepareDatacards/prepareDatacards_1l_1tau_1l_1tau_mvaOutput_Legacy_6_disabled.root"}, # mT_lep is from lep_pt
    "2los_1tau"              : {"channel" : "1l_1tau", "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/2los_1tau/prepareDatacards/prepareDatacards_2los_1tau_mvaOutput_legacy.root"},                # mT_lep is from lep_pt
    ##############################
    "2l_2tau"                : {"channel" : "2l_2tau", "shapes" : "/home/veelken/public/tthAnalysis/datacards/prepareDatacards_2l_2tau_mvaOutput_final_2018.root"},
    "4l_0tau"                : {"channel" : "4l_0tau", "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/4l/prepareDatacards/prepareDatacards_4l_OS_mva_4l.root"},                                     # 25Dec has CR to plot
    "3l_1tau"                : {"channel" : "3l_1tau", "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/3l_1tau/prepareDatacards/prepareDatacards_3l_1tau_OS_mvaOutput_legacy.root"},                 # 25Dec has CR to plot
    ###########################
    ### there is only 2018 while we cannot check with Oviedo
    #"3l_cr_eee"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_eee.root"},
    #"3l_cr_eem"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_eem.root"},
    #"3l_cr_emm"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_emm.root"},
    #"3l_cr_mmm"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_mmm.root"},
    ###########################
    "4l_cr"                   : {"channel" : "4lctrl",  "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/4lctrl/prepareDatacards/prepareDatacards_4lctrl_OS_control.root"},

}

cards_SVA = {
    ### there is only 2018 while we cannot check with Oviedo
    "2lss_0tau_cr"        : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_cr.root"},
    "2lss_0tau_ee_hj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_hj_neg.root"},
    "2lss_0tau_ee_hj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_hj_pos.root"},
    "2lss_0tau_ee_lj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_lj_neg.root"},
    "2lss_0tau_ee_lj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_ee_lj_pos.root"},
    "2lss_0tau_em_hj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_hj_neg.root"},
    "2lss_0tau_em_hj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_hj_pos.root"},
    "2lss_0tau_em_lj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_lj_neg.root"},
    "2lss_0tau_em_lj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_em_lj_pos.root"},
    "2lss_0tau_mm_hj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_hj_neg.root"},
    "2lss_0tau_mm_hj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_hj_pos.root"},
    "2lss_0tau_mm_lj_neg" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_lj_neg.root"},
    "2lss_0tau_mm_lj_pos" : {"channel" : "2lss_0tau", "shapes" : "/home/acaan/ttHAnalysis/2018/2lss_0tau_central_DNN_legacy_IHEP_DNN_2017_20Dec2019/datacards/2lss/prepareDatacards/prepareDatacards_2lss_mass_2L_mm_lj_pos.root"},
    ######################
    ## 3l
    ###########################
    #### mT_lep is from lep_pt
    "2lss_1tau"              : {"channel" : "2lss_1tau", "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_2lss_1tau_2018/datacards/2lss_1tau/prepareDatacards/prepareDatacards_2lss_1tau_sumOS_mTauTauVis1.root"},
    ######################
    "0l_2tau"                : {"channel" : "0l_2tau", "shapes" : "/home/arun/ttHAnalysis/2018/2019Dec23/datacards/0l_2tau/prepareDatacards/prepareDatacards_0l_2tau_0l_2tau_mTauTau.root"},
    "1l_2tau"                : {"channel" : "1l_2tau", "shapes" : "/home/arun/ttHAnalysis/2018/2019Dec23/datacards/1l_2tau/prepareDatacards/prepareDatacards_1l_2tau_mTauTauVis.root"},
    "1l_1tau"                : {"channel" : "1l_1tau", "shapes" : "/home/arun/ttHAnalysis/2018/2019Dec23/datacards/1l_1tau/prepareDatacards/prepareDatacards_1l_1tau_1l_1tau_mTauTau_disabled.root"},
    "2los_1tau"              : {"channel" : "1l_1tau", "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/2los_1tau/prepareDatacards/prepareDatacards_2los_1tau_mTauTauVis.root"},
    ##############################
    "2l_2tau"                : {"channel" : "2l_2tau", "shapes" : "/home/veelken/ttHAnalysis/2018/2019Dec23/datacards/2l_2tau/prepareDatacards/prepareDatacards_2l_2tau_lepdisabled_taudisabled_sumOS_mTauTauVis.root"},
    "4l_0tau"                : {"channel" : "4l_0tau", "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/4l/prepareDatacards/prepareDatacards_4l_OS_mass_4L.root"},                  # 25Dec has CR to plot
    "3l_1tau"                : {"channel" : "3l_1tau", "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/3l_1tau/prepareDatacards/prepareDatacards_3l_1tau_OS_EventCounter.root"},   # 25Dec has CR to plot
    ###########################
    ### there is only 2018 while we cannot check with Oviedo
    #"3l_cr_eee"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_eee.root"},
    #"3l_cr_eem"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_eem.root"},
    #"3l_cr_emm"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_emm.root"},
    #"3l_cr_mmm"             : {"channel" : "3lctrl",  "shapes" : "/home/acaan/ttHAnalysis/2018/legacy_fullSyst_3l_0tau_CR_2018/datacards/3lctrl/prepareDatacards/prepareDatacards_3lctrl_OS_control_mmm.root"},
    ###########################
    "4l_cr"                   : {"channel" : "4lctrl",  "shapes" : "/home/karl/ttHAnalysis/2018/2019Dec24/datacards/4lctrl/prepareDatacards/prepareDatacards_4lctrl_OS_control.root"},

}

for era in eras_to_do :
    if make_cards :
        for key in cards_MVA :
            print (key)
            print (cards_MVA[key])
            cmd = "WriteDatacards.py "
            cmd += "--inputShapes %s " % (cards_MVA[key]["shapes"].replace("2018", era))
            cmd += "--channel %s "     % (cards_MVA[key]["channel"].replace("2018", era))
            cmd += "--cardFolder %s "  % output_cards
            cmd += "--noX_prefix  "
            if not "ctrl" in key :
                cmd += "--no_data "
            cmd += "--era %s" % str(era)
            cmd += " --output_file %s/ttH_%s_%s" % (output_cards, key, era)
            # cmd += "--shapeSyst " ### for first tests
            runCombineCmd(cmd)
    #######################
    # combine cards to make plots -- the order of lists of flavours is important
    if "3l_cr_eee" in list(cards_MVA.keys()) :
        cmd = "combineCards.py "
        for flavor in ["eee", "eem", "emm", "mm"] :
            cmd += " 3lctr_%s=ttH_3l_cr_%s_%s.txt" % (flavor, flavor, era)
        cmd += " > ttH_3l_cr_%s.txt" % era
        runCombineCmd(cmd, output_cards)
    #
    if "2lss_0tau_ee_Restnode" in list(cards_MVA.keys()) :
        for node in ["Rest", "ttH", "ttW", "tHQ"] :
          cmd = "combineCards.py "
          for flavor in ["ee", "em", "mm"] :
            cmd += " ttH_2lss_0tau_%s_%snode=ttH_2lss_0tau_%s_%snode_%s.txt" % (flavor, node, flavor, node, era)
          cmd += " > ttH_2lss_0tau_%snode_%s.txt" % (node, era)
          runCombineCmd(cmd, output_cards)
    #
    if "3l_0tau_rest_eee" in list(cards_MVA.keys()) :
        for node in ["ttH", "tH"] :
          cmd = "combineCards.py "
          for flavor in ["bt", "bl"] :
            cmd += " ttH_3l_0tau_%s_%s=ttH_3l_0tau_%s_%s_%s.txt" % (node, flavor, node, flavor, era)
          cmd += " > ttH_3l_0tau_%s_%s.txt" % (node, era)
          runCombineCmd(cmd, output_cards)
        cmd = "combineCards.py "
        for flavor in ["eee", "eem", "emm", "mmm"] :
            cmd += " ttH_3l_0tau_rest_%s=ttH_3l_0tau_rest_%s_%s.txt" % (flavor, flavor, era)
        cmd += " > ttH_3l_0tau_rest_%s.txt" % (era)
        runCombineCmd(cmd, output_cards)
    #
    if "2lss_1tau_rest" in list(cards_MVA.keys()) :
        cmd = "combineCards.py "
        for node in ["ttH", "tH", "rest"] :
            cmd += "ttH_2lss_1tau_%s=ttH_2lss_0tau_%s_%s.txt" % (node, node, era)
        cmd += " > ttH_2lss_1tau_%s.txt" % (era)
        runCombineCmd(cmd, output_cards)
    ##################################
    # combine all cards to make fits / era
    cmd = "combineCards.py "
    for key in list(cards_MVA.keys()) :
        cmd += " ttH_%s=ttH_%s_%s.txt" % (key, key, era)
    cmd += " > ttH_multilep_%s.txt" % (era)
    runCombineCmd(cmd, output_cards)
############################################
# combine all cards to make fits
cmd = "combineCards.py "
for era in eras_to_do :
    cmd += " ttH_%s= ttH_multilep_%s.txt" % (era, era)
cmd += " > ttH_multilep.txt"
