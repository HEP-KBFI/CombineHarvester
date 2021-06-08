#!/usr/bin/env python

import os, subprocess, sys, time, math, re, shlex
import ROOT
from optparse import OptionParser
from collections import OrderedDict
from subprocess import Popen, PIPE
from CombineHarvester.ttH_htt.data_manager import runCombineCmd, splitPath, PrintTables

from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "--inputShapes", type="string", dest="inputShapes",
    help="PrepareDatacard from which run combine and draw the shapes from (full or relative path)"
    )
parser.add_option(
    "--odir", type="string", dest="odir",
    help="Directory for the output. If it is not entered it is done on the same folders that contains the inputCard",
    default="none"
    )
parser.add_option(
    "--channel", type="string", dest="channel",
    help="Name of the category as it is appear on the input file",
    default="1l_2tau"
    )
parser.add_option(
    "--unblind", action="store_true", dest="unblind",
    help="Do subcategories from multilepton cards ",
    default=False
    )
parser.add_option(
    "--doImpacts", action="store_true", dest="doImpacts",
    help="Do the postfit plot",
    default=False
    )
parser.add_option(
    "--doGOF", action="store_true", dest="doGOF",
    help="Do the postfit plot",
    default=False
    )
parser.add_option(
    "--doPostFit", action="store_true", dest="doPostFit",
    help="Do the postfit plot",
    default=False
    )
parser.add_option(
    "--doPreFit", action="store_true", dest="doPreFit",
    help="Do the prefit plot",
    default=False
    )
parser.add_option(
    "--notRedoWS", action="store_true", dest="notRedoWS",
    help="If you already did this once for a given input and are only polishing the plot layout there is no need of doing the again. This option ",
    default=False
    )
parser.add_option("--analysis",       type="string",       dest="analysis",    
    help="Analysis type = 'ttH' or 'HH' (to know what to take as Higgs procs and naming convention of systematics), Default ttH", 
    default="ttH"
    )
parser.add_option("--era",       type="string",       dest="era",    
    help="Era to consider (important for list of systematics and labeling). Default: 2017", 
    default="2017"
    )
parser.add_option("--shapeSyst",      action="store_true", dest="shapeSyst",   
    help="Do apply the shape systematics. Default: False", 
    default=False
    )
parser.add_option(
    "--plainBins", action="store_true", dest="plainBins",
    help="Draw the plot without rebining the X-axis as originally proposed (just as plain list of bins)",
    default=False
    )
parser.add_option(
    "--doLimits", action="store_true", dest="doLimits",
    help="Compute the limits",
    default=False
    )
parser.add_option(
    "--doPostFitYields", action="store_true", dest="doPostFitYields",
    help="output a files with a tex-like table of PostFit yields",
    default=False
    )
parser.add_option(
    "--doPreFitYields", action="store_true", dest="doPreFitYields",
    help="output a files with a tex-like table of PreFit yields",
    default=False
    )
(options, args) = parser.parse_args()

#ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
sys.stdout.flush()

channel          = options.channel
doPostFit        = options.doPostFit
doPreFit         = options.doPreFit
doLimits         = options.doLimits
doImpacts        = options.doImpacts
doGOF            = options.doGOF
plainBins        = options.plainBins
unblind          = options.unblind
doPostFitYields  = options.doPostFitYields
doPreFitYields   = options.doPreFitYields

fileDatacard, pathDatacard = splitPath(options.inputShapes)
fileDatacard = fileDatacard.replace(".root","").replace(".txt","")

odir = options.odir
if odir == "none" : 
    odir = pathDatacard

fileDat = fileDatacard.replace("prepareDatacards","datacard")
if options.shapeSyst : 
    fileDat += "_wShapeSyst"

if not options.notRedoWS :
    cmd = "WriteDatacards.py "
    cmd += " --inputShapes %s/%s.root"  % (pathDatacard, fileDatacard) 
    cmd += " --channel %s"  % channel
    cmd += " --cardFolder %s" % odir 
    cmd += " --output_file %s/%s"  % (odir, fileDat) 
    if options.shapeSyst : cmd += " --shapeSyst"
    cmd += " --noX_prefix"
    #cmd += " --only_ttH_sig"
    runCombineCmd(cmd)
    print ("created datacard: " + "%s/%s.txt" % (odir, fileDat) )

    cmd = "text2workspace.py"
    cmd += " %s.txt"        % fileDat
    cmd += " -o %s_WS.root" % fileDat
    runCombineCmd(cmd, odir)
    print ("created workspace: " + "%s/%s_WS.root" % (odir, fileDat) )
elif os.path.isfile("%s_WS.root" % fileDat) :
    print ("You need to produce the workspace, remove notRedoWS from command line")

if options.doLimits :
    for opt in ["Syst", "noSyst"] :
        logFile = "%s_%s_unblind%s.log" % (fileDat, opt, unblind)
        cmd = "combine -M AsymptoticLimits -m 125"
        if not unblind : cmd += " -t -1 --run blind" 
        if opt == "noSyst" : cmd += " -S 0"
        cmd += " %s_WS.root" % fileDat
        runCombineCmd(cmd, odir, logFile)

if options.doImpacts :
    # TODO: add to plotImpacts.py an option to skip bin uncertainties 
    for typefit in ["--doInitialFit", "--robustFit 1 --doFits"] :
        cmd = "combineTool.py -M Impacts -m 125"
        cmd += " -d %s_WS.root" % fileDat
        if not unblind : cmd += " -t -1 " 
        cmd += " --expectSignal 1 --allPars --parallel 8 "  
        cmd += typefit
        runCombineCmd(cmd, odir)
    cmd = "combineTool.py -M Impacts -m 125"
    cmd += " -d %s_WS.root" % fileDat
    cmd += " -o impacts.json"   
    runCombineCmd(cmd, odir)
    cmd = "plotImpacts.py -i impacts.json"   
    if not unblind : cmd += " --blind"
    cmd += " -o impacts_%s" % fileDat
    runCombineCmd(cmd, odir)
    print ("Saved: " + "%s/impacts_%s.pdf" % (odir, fileDat) )

if options.doGOF :
    cmd = "combine -M GoodnessOfFit --algo=saturated --fixedSignalStrength=1"
    cmd += " %s_WS.root" % fileDat  
    runCombineCmd(cmd, odir)
    cmd = "combine -M GoodnessOfFit --algo=saturated --fixedSignalStrength=1"
    cmd += " %s_WS.root" % fileDat 
    cmd += " -t 1000 -s 12345 --saveToys --toysFreq" 
    runCombineCmd(cmd, odir)
    cmd = "combineTool.py -M CollectGoodnessOfFit"
    cmd += " --input higgsCombineTest.GoodnessOfFit.mH120.root higgsCombineTest.GoodnessOfFit.mH120.12345.root"
    cmd += " -o GoF_saturated.json" 
    runCombineCmd(cmd, odir)
    cmd = "plotGof.py"
    cmd += " --statistic saturated --mass 120.0 GoF_saturated.json "
    cmd += " -o GoF_saturated_%s" % fileDat
    runCombineCmd(cmd, odir)
    print ("Saved: " + "%s/GoF_saturated_%s.pdf" % (odir, fileDat) )

if doPreFitYields or doPostFitYields :
    cmd = "combineTool.py -M FitDiagnostics %s_WS.root" % fileDat
    runCombineCmd(cmd, odir)
    print ("the diagnosis that input Havester is going to be on fitDiagnostics.Test.root or fitDiagnostics.root depending on your version of combine -- check if that was the case you have a crash!")
    cmd = "python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py"
    cmd += " -a fitDiagnostics.Test.root -g plots.root  -p r_ttH"
    runCombineCmd(cmd, odir)
    import CombineHarvester.CombineTools.ch as ch
    ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')
    print ("Retrieving yields from workspace: ", "%s/%s_WS.root" % (odir, fileDat))
    fin = ROOT.TFile("%s/%s_WS.root" % (odir, fileDat))
    wsp = fin.Get('w')
    cmb = ch.CombineHarvester()
    cmb.SetFlag("workspaces-use-clone", True)
    ch.ParseCombineWorkspace(cmb, wsp, 'ModelConfig', 'data_obs', False)
    print ("datacard parsed")
    if doPostFitYields :
        cmb.UpdateParameters(rfr)
        print (' Parameters updated ')
    outYields = "%s/%s" % (odir, fileDat)
    if doPostFitYields : outYields += "_postfit"
    if doPreFitYields  : outYields += "_prefit"
    outYields += ".tex"
    filey = open(outYields, "w")
    # TODO: simplify the function with master10X KBFI naming conventions only
    #blindedOutput = False
    #if unblind : blindedOutput = True
    labels = [channel]
    typeChannel = 'tau'
    if doPreFitYields  : PrintTables(cmb, tuple(), filey, unblind, labels, typeChannel)
    if doPostFitYields :  PrintTables(cmb, (rfr, 500), filey, unblind, labels, typeChannel)
    print ("the yields are on this file: " + outYields)

if (doPostFit or doPreFit) : 
    # to have Totalprocs computed
    cmd = "combineTool.py -M FitDiagnostics %s_WS.root" % fileDat
    runCombineCmd(cmd, odir)
    print ("the diagnosis that input Havester is going to be on fitDiagnostics.Test.root or fitDiagnostics.root depending on your version of combine -- check if that was the case you have a crash!")
 
    shapeDatacard    = "%s_shapes.root" % fileDat
    if doPostFit : 
        shapeDatacard = shapeDatacard.replace(".root", "_postfit.root")
        print ("[WARNING]: the postfit plot will be done for this channel, extracting only signal (as defined on the input datacard) and without any BKG floating")
        print ("To do it for ttH channel with full fitting options please refer to: ")
    if doPreFit  : 
        shapeDatacard = shapeDatacard.replace(".root", "_prefit.root")
    if plainBins : 
        shapeDatacard = shapeDatacard.replace(".root", "_plainBins.root")

    cmd = "PostFitShapesFromWorkspace "
    cmd += " --workspace %s_WS.root" % fileDat
    cmd += " --o %s" % shapeDatacard
    cmd += " --sampling --print " 
    if doPostFit         : cmd += " --postfit "
    if not plainBins : cmd += " -d %s.txt"        % fileDat
    runCombineCmd(cmd, odir)
    print ("created " + odir + "/" + shapeDatacard )

    cmd = "makePostFitPlots.py "
    cmd += " --inputDatacard %s/%s" % (odir, shapeDatacard)
    if not plainBins : cmd += " --original %s/%s.txt" % (odir, fileDat) 
    cmd += " --channel %s" % channel 
    ##if unblind           : cmd += " --unblind "
    if doPostFit         : cmd += " --doPostFit "
    runCombineCmd(cmd)
    print ("created plot " + odir + "/" + shapeDatacard.replace(".root", "*.pdf")  )