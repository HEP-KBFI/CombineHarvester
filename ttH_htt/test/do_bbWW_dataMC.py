#!/usr/bin/env python
import os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
from io import open
import glob

exec(open(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager.py").read())
# for the runCombineCmd

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath",  type="string", dest="inputPath",  help="Full path of where prepareDatacards.root are ")
parser.add_option("--outputpath", type="string", dest="outputpath", help="name of prepareDatacards.root. In not given will pick all from the inputPath", default="none")
parser.add_option("--channel",    type="string", dest="channel",    help="By now \"2l_0tau\" or \"1l_0tau\" ", default="none")
parser.add_option("--era",        type="int",    dest="era",        help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.", default=0)
(options, args) = parser.parse_args()

output_cards = options.outputpath
input_files  = options.inputPath
era          = options.era
channel      = options.channel

## agreed that for data/MC files the signal should bt 400 GeV resonace
signal_type = "res"
mass         = "spin0_400"
mergeSL   = False
makeCards = True
makePlots = True
makeHadd  = False
makePlotsOnly = False

if era == 0 :
    eras_to_do = [ "2016" , "2017", "2018" ]
else :
    eras_to_do = [ str(era) ]

types_plot = []

if channel == "2l_0tau" :
    # prepareDatacards_hh_bb2l_hh_bb2l_OS_cat_mm_Hbb_boosted_jet1_eta.root
    HHtype      = "bbWW"
    filebegin = "prepareDatacards_hh_bb2l_hh_bb2l_OS_"
    categories_list_bins =  [
     "cat_ee_1b",
     "cat_em_1b",
     "cat_mm_1b",
     "cat_ee_2b",
     "cat_em_2b",
     "cat_mm_2b",
     "cat_ee_Hbb_boosted",
     "cat_em_Hbb_boosted",
     "cat_mm_Hbb_boosted"
    ]
    for_data_MC_plots = [
    "jet1_pt",
    "jet1_eta",
    "lep1_pt",
    "lep1_eta",
    "jet2_pt",
    "jet2_eta",
    "lep2_pt",
    "lep2_eta"
    ]
    for typeMVA in for_data_MC_plots :
      for typyCat in categories_list_bins :
        types_plot = types_plot + [ "%s%s_%s" % (filebegin, typyCat, typeMVA) ]

elif channel == "1l_0tau" :
    # prepareDatacards_hh_bb1l_hh_bb1l_lep1_pt_WjjFat_LP_m.root
    HHtype      = "bbWW"
    filebegin   = "prepareDatacards_hh_bb1l_hh_bb1l_"
    if mergeSL :
        categories_list_bins =  [
        "_HbbFat_WjjRes_XXX_e",
        "_Res_XXX_1b_e",
        "_Res_XXX_2b_e",
        "_HbbFat_WjjRes_XXX_m",
        "_Res_XXX_1b_m",
        "_Res_XXX_2b_m",
        ]

    else :
        categories_list_bins =  [
        "_HbbFat_WjjRes_allReco_e",
        "_Res_allReco_1b_e",
        "_Res_allReco_2b_e",
        "_HbbFat_WjjRes_allReco_m",
        "_Res_allReco_1b_m",
        "_Res_allReco_2b_m",
        "_HbbFat_WjjRes_MissJet_e",
        "_Res_MissWJet_1b_e",
        "_Res_MissWJet_2b_e",
        "_HbbFat_WjjRes_MissJet_m",
        "_Res_MissWJet_1b_m",
        "_Res_MissWJet_2b_m",
        ]

    for_data_MC_plots = [
    "jet1_pt",
    "jet1_eta",
    "lep1_pt",
    "lep1_eta",
    "jet2_pt",
    "jet2_eta"
    ]
    for typeMVA in for_data_MC_plots :
      for typyCat in categories_list_bins :
        types_plot = types_plot + [ "%s%s%s" % (filebegin, typeMVA, typyCat) ]
else :
    print ("Channel %s not implemented" % channel)
    sys.exit()

if mergeSL and makeHadd :
    for cat in categories_list_bins :
      for plot in for_data_MC_plots :
        cmd = "rm %s%s%s.root" % ( filebegin, plot, cat.replace("_XXX_", "_") )
        runCombineCmd(cmd, input_files)
        cmd = "hadd %s%s%s.root %s%s%s.root %s%s%s.root" % ( filebegin, plot, cat.replace("_XXX_", "_"), filebegin, plot, cat.replace("_XXX_", "_allReco_"), filebegin, plot, cat.replace("_XXX_", "_MissWJet_") )
        runCombineCmd(cmd, input_files, "%s%s%s.log" % ( filebegin, plot, cat ) )

for era in eras_to_do :
    for kk, key in enumerate(types_plot) :
        #if kk > 0 : break

        toRead = key
        if mergeSL :
            toRead = key.replace("_XXX_", "_")
        print ( toRead )

        combine_output_cards = "%s/%s" % (output_cards, toRead.replace(filebegin, "HH_"))
        combine_output_cards_final = "%s/%s_%s_%s_%s" % (output_cards, toRead.replace(filebegin, "HH_"), HHtype, signal_type, mass)

        if makeCards and not makePlotsOnly :
            cmd = "WriteDatacards.py "
            cmd += "--inputShapes %s/%s.root " % (input_files, toRead.replace("2018", era))
            cmd += "--channel %s "     % channel
            cmd += "--cardFolder %s "  % output_cards
            cmd += "--noX_prefix --analysis HH  "
            #if not "ctrl" in cards_to_do[key]["channel"]  :
            #    cmd += " --no_data "
            cmd += " --era %s "              % str(era)
            cmd += " --output_file %s"       % combine_output_cards
            cmd += " --signal_type %s "      % signal_type
            cmd += " --mass %s "             % mass
            cmd += " --HHtype %s "           % HHtype
            runCombineCmd(cmd, '.', "%s.log" % combine_output_cards_final)
            print ("output card/log saved on: %s.txt/root/log" % combine_output_cards_final )

        if makePlots or makePlotsOnly:

            FolderOut = "%s/results/" % (output_cards)
            combine_output_cards_final_only = combine_output_cards_final.split("/")[len(combine_output_cards_final.split("/")) - 1]
            if not makePlotsOnly :
                cmd = "mkdir %s" % FolderOut
                runCombineCmd(cmd)

                # make only HH be considered signal (independent of the card marking)
                float_sig_rates = " --PO 'map=.*/.*hh.*:r_HH[1,-20,100]' "

                cmd = "text2workspace.py"
                cmd += " %s.txt  " % combine_output_cards_final_only
                cmd += " -o %s/%s_WS.root" % (FolderOut, combine_output_cards_final_only)
                cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
                cmd += " %s" % float_sig_rates
                runCombineCmd(cmd, output_cards)
                print ("done %s/%s_WS.root" % (FolderOut, combine_output_cards_final_only))

                cmd = "combineTool.py -M FitDiagnostics "
                cmd += " %s_WS.root" % combine_output_cards_final_only
                #if blinded :
                #    cmd += " -t -1 "
                cmd += " --saveShapes --saveWithUncertainties "
                cmd += " --saveNormalization "
                cmd += " --skipBOnlyFit "
                cmd += " -n _shapes_combine_%s" % combine_output_cards_final_only
                runCombineCmd(cmd, FolderOut)
            fileShapes = glob.glob("%s/fitDiagnostics_shapes_combine_%s*root" % (FolderOut, combine_output_cards_final_only))[0]
            print ( "done %s" % fileShapes )

            savePlotsOn = "%s/plots/" % (output_cards)
            cmd = "mkdir %s" % savePlotsOn
            runCombineCmd(cmd)

            plainBins = False
            cmd = "python test/makePlots.py "
            cmd += " --input  %s" % fileShapes
            cmd += " --odir %s" % savePlotsOn
            #if doPostFit         :
            #    cmd += " --postfit "
            if not plainBins :
                cmd += " --original %s.root"        % (combine_output_cards_final)
            cmd += " --era %s" % str(era)
            cmd += " --nameOut %s" % combine_output_cards_final_only
            cmd += " --do_bottom "
            cmd += " --channel %s" % channel
            cmd += " --HH --binToRead HH_%s --binToReadOriginal  HH_%s " % (channel, channel)
            cmd += "--nameLabel %s --labelX %s" % (toRead.replace(filebegin, ""), toRead.replace(filebegin, ""))
            #if not blinded         :
            cmd += " --unblind  "
            cmd += " --signal_type %s "      % signal_type
            cmd += " --mass %s "             % mass
            cmd += " --HHtype %s "           % HHtype
            plotlog = "%s/%s_plot.log" % (savePlotsOn, combine_output_cards_final_only)
            runCombineCmd(cmd, '.', plotlog)

            didPlot = False
            for line in open(plotlog):
                if '.pdf' in line and "saved" in line :
                    print(line)
                    didPlot = True
                    break
            if didPlot == False :
                print ("!!!!!!!!!!!!!!!!!!!!!!!! The makePlots did not worked, to debug please check %s to see up to when the script worked AND run again for chasing the error:" % fileInfo)
                print(cmd)
                sys.exit()
