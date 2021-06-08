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
parser.add_option("--variables", type="string", dest="variables", help="Add convention to file name", default="teste")
parser.add_option("--BINtype", type="string", dest="BINtype", help="regular / ranged / quantiles", default="quantiles")
parser.add_option("--do_signalFlat", action="store_true", dest="do_signalFlat", help="whether you want to make signal flat or total bkg flat", default=False)
parser.add_option("--output_path", type="string", dest="output_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--prepareDatacards_path", type="string", dest="prepareDatacard_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--doPlots", action="store_true", dest="doPlots", help="If you call this will not do plots with repport", default=False)
parser.add_option("--drawLimitsOnly", action="store_true", dest="drawLimitsOnly", help="If you call this will not do plots with repport", default=False)
parser.add_option("--doLimitsOnly", action="store_true", dest="doLimitsOnly", help="If you call this will not do plots with repport", default=False)
parser.add_option("--BDTfor", dest="BDTfor", help="type of BDT to be considered", default="SM")
parser.add_option("--shapeSyst",      action="store_true", dest="shapeSyst",   help="Do apply the shape systematics. Default: False", default=False)
parser.add_option("--no_data",      action="store_true", dest="no_data",   help="use data or not. Default: False", default=False)
parser.add_option(
    "--signal_type",    type="string",       dest="signal_type",
    help="Options: \"nonresLO\" | \"nonresNLO\" | \"res\" ",
    default="nonresLO"
    )
parser.add_option(
    "--mass",           type="string",       dest="mass",
    help="Options: \n nonresNLO = it will be ignored \n nonresLO = \"SM\", \"BM12\", \"kl_1p00\"... \n \"spin0_900\", ...",
    default="kl_1p00"
    )
parser.add_option(
    "--HHtype",         type="string",       dest="HHtype",
    help="Options: \"bbWW\" | \"multilep\" | \"bbWWsl\" | \"bbWWdl\" ",
    default="bbWW"
    )
parser.add_option(
    "--era", type="int",
    dest="era",
    help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.",
    default=2016
    )
parser.add_option(
    "--subcats",
    choices = ["Res_allReco", "boosted_semiboosted", "one_missing_boosted", "one_missing_resolved", "semiboosted_boosted_combine", "singleCat",
               "resolved_singleCat", "boosted_singleCat", "resolved_2b_nonvbf", 'boosted', "resolved_2b_vbf", 'resolved_1b', 'HH_resolved_1b', 'HH_resolved_2b_vbf',
               'HH_resolved_2b_nonvbf', 'HH_boosted', 'TT_resolved', 'TT_boosted', 'W_resolved', 'W_boosted', 'DY_resolved', 'DY_boosted', 'SingleTop_resolved', 'SingleTop_boosted','Other', ''],
    dest="subcats",
    help="subcategory to be considered in rebinning",
    default=''
    )
(options, args) = parser.parse_args()

doLimitsOnly   = options.doLimitsOnly
drawLimitsOnly = options.drawLimitsOnly
doPlots    = options.doPlots
channel    = options.channel
BINtype    = options.BINtype
do_signalFlat = options.do_signalFlat
signal_type  = options.signal_type
mass         = options.mass
HHtype       = options.HHtype
era          = options.era
local        = options.output_path
mom          = options.prepareDatacard_path
BDTfor =  options.BDTfor
in_more_subcats = options.subcats
shape            = options.shapeSyst
no_data          = options.no_data
## HH
if channel == "2l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2l_0tau_datacards.py")
if channel == "1l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_1l_0tau_datacards.py")

info = read_from(in_more_subcats, BDTfor)
print ("Cards to rebin from %s" % channel)

sendToCondor = False
ToSubmit = " "
if sendToCondor :
    ToSubmit = " --job-mode condor --sub-opt '+MaxRuntime = 1800' --task-name"

sources           = []
bdtTypesToDo      = []
bdtTypesToDoLabel = []
bdtTypesToDoFile  = []
sourcesCards      = []

#local = info["local"]
import shutil,subprocess
proc=subprocess.Popen(["mkdir %s" % local],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()

mom_datacards = "%s/datacards_rebined/" % local
proc=subprocess.Popen(["mkdir %s" % mom_datacards],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()

print (info["bdtTypes"])

counter=0
for ii, bdtType in enumerate(info["bdtTypes"]) :
    fileName = mom   + "/addSystFakeRates_" + info["ch_nickname"] + "_" + bdtType + ".root"
    source   = local + "/addSystFakeRates_" + info["ch_nickname"] + "_" + bdtType
    print (fileName)
    if os.path.isfile(fileName) :
        proc              = subprocess.Popen(['cp ' + fileName + " " + local],shell=True,stdout=subprocess.PIPE)
        out = proc.stdout.read()
        sources           = sources + [source]
        bdtTypesToDo      = bdtTypesToDo +[channel+" "+bdtType]
        bdtTypesToDoLabel = bdtTypesToDoLabel + [channel+" "+bdtType]
        bdtTypesToDoFile  = bdtTypesToDoFile+[bdtType]
        ++counter
        print ("rebinning ", sources[counter])
    else : print ("does not exist ",source)
print ("I will rebin", bdtTypesToDoLabel,"(",len(sources),") BDT options")

if BINtype == "regular" or BINtype == "ranged" :
    binstoDo = info["nbinRegular"]
if BINtype == "quantiles" :
    binstoDo = info["nbinQuant"]
if BINtype == "none" :
    binstoDo=np.arange(1, info["originalBinning"])
print binstoDo

### first we do one datacard.txt / bdtType
for nn, source in enumerate(sources) :
    if BINtype == "regular" :
        outfile = "%s" % (source.replace("addSystFakeRates_", "datacard_"))
    if BINtype == "quantiles" or BINtype == "ranged":
        outfile = "%s_%s" % (source.replace("addSystFakeRates_", "datacard_"), BINtype )

    cmd = "WriteDatacards.py "
    cmd += "--inputShapes %s.root " % (source)
    cmd += "--channel %s " % channel
    cmd += "--output_file %s " % (outfile)
    cmd += "--noX_prefix --era %s --analysis HH " % (era) # --only_ttH_sig --only_BKG_sig --only_tHq_sig --fake_mc
    if no_data:
        cmd += '--no_data'
    ## TODO add only_HH_sig in WriteDatacards
    cmd += " --signal_type %s "      % signal_type
    cmd += " --mass %s "             % mass
    cmd += " --HHtype %s "           % HHtype
    cmd += " --subcat %s "           % options.subcats
    if shape:
        cmd += " --shapeSyst %s --forceModifyShapes "        % shape
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

nameOutFileAdd = ""
if BINtype=="none" :
    nameOutFileAdd =  "bins_none"
if BINtype=="regular" or options.BINtype == "mTauTauVis":
    nameOutFileAdd =  "bins"
if BINtype=="ranged" :
    nameOutFileAdd =  "bins_ranged"
if BINtype=="quantiles" :
    nameOutFileAdd = "bins_quantiles"

colorsToDo=['r','g','b','m','y','c', 'fuchsia', "peachpuff",'k','orange','y','c'] #['r','g','b','m','y','c','k']
#########################################
#if not (drawLimitsOnly or doLimitsOnly) :
if True:
    ## make rebinned datacards
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.title(BINtype+" in sum of BKG ")
    lastQuant=[]
    xmaxQuant=[]
    xminQuant=[]
    bin_isMoreThan02 = []
    maxplot = -99.
    ncolor = 0
    ncolor2 = 0
    linestyletype = "-"
    merge_Wjets = False
    if channel == '2l_0tau':
        merge_Wjets = True
    for nn, sourceL in enumerate(sourcesCards) :
        print ( "rebining %s" % sourceL )
        errOcont = rebinRegular(
            sourceL,
            binstoDo,
            BINtype,
            do_signalFlat,
            merge_Wjets,
            info["originalBinning"],
            doPlots,
            bdtTypesToDo[nn],
            mom_datacards,
            nameOutFileAdd,
            info["withFolder"]
            )
        if max(errOcont[2]) > maxplot :
            maxplot = max(errOcont[2])
        print bdtTypesToDo[nn]
        lastQuant=lastQuant+[errOcont[4]]
        xmaxQuant=xmaxQuant+[errOcont[5]]
        xminQuant=xminQuant+[errOcont[6]]
        bin_isMoreThan02 = bin_isMoreThan02 + [errOcont[7]]

        print (binstoDo,errOcont[2])
        plt.plot(binstoDo, errOcont[2], color=colorsToDo[ncolor],linestyle=linestyletype,label=bdtTypesToDo[nn].replace("ttH_1l_2tau","BDT PAS").replace("output_NN_","NN_").replace("_ttH_tH_3cat_","").replace("1l_2tau","").replace("2lss_1tau_","").replace("_1tau","").replace("2lss","").replace("__","_"))  #.replace("3l_0tau output_NN_3l_ttH_tH_3cat_v8_", "") ) # ,label=bdtTypesToDo[nn]
        ncolor = ncolor + 1
        if ncolor == 10 :
            ncolor = 0
            ncolor2 = ncolor2 + 1
            if ncolor2 == 0 : linestyletype = "-"
            if ncolor2 == 1 : linestyletype = "-."
            if ncolor2 == 2 : linestyletype = ":"
        ax.set_xlabel('nbins')
    maxplot = 1.2
    plt.axis((min(binstoDo),max(binstoDo),0,maxplot*1.2))
    ax.set_ylabel('err/content last bin')
    ax.legend(loc='best', fancybox=False, shadow=False, ncol=1, fontsize=8)
    plt.grid(True)
    namefig = local + '/' + options.variables + '_'+ signal_type + '_' + mass + '_' + options.subcats + '_ErrOcont_' + BINtype + '_do_signalFlat_' + str(do_signalFlat) +'_'+ BDTfor+'_'+ str(era)+'.png'
    fig.savefig(namefig)
    print ("saved",namefig)
    print (bin_isMoreThan02)
    #########################################
    ## plot quantiles boundaries
    if BINtype == "quantiles" :
        ncolor = 0
        fig, ax = plt.subplots(figsize=(5, 5))
        plt.title(BINtype+" binning "+options.variables)
        linestyletype = "-"
        for nn,source in enumerate(sources) :
            print (len(binstoDo),len(lastQuant[nn-1]))
            plt.plot(binstoDo,lastQuant[nn], color=colorsToDo[ncolor],linestyle=linestyletype)
            plt.plot(binstoDo,lastQuant[nn], color=colorsToDo[ncolor],linestyle=linestyletype,marker='o') # ,label=bdtTypesToDo[nn]
            plt.plot(binstoDo,xmaxQuant[nn], color=colorsToDo[ncolor],linestyle=linestyletype,marker='x')
            plt.plot(binstoDo,xminQuant[nn], color=colorsToDo[ncolor],linestyle=linestyletype,marker='.')
            ncolor = ncolor + 1
            if ncolor == 10 or ncolor == 20:
                ncolor = 0
                if ncolor == 10 : linestyletype = "--"
                if ncolor == 20 : linestyletype = ":"
        ax.set_xlabel('nbins')
        ax.set_ylabel('err/content last bin')
        plt.axis((min(binstoDo),max(binstoDo),0,1.0))
        line_up, = plt.plot(binstoDo, 'o-', color='k',label="last bin low")
        line_down, = ax.plot(binstoDo, 'x--', color='k',label="Max")
        line_d, = ax.plot(binstoDo, '.--', color='k',label="Min")
        legend1 = plt.legend(handles=[line_up, line_down, line_d], loc='best', fontsize=8)
        ax.set_ylabel('boundary')
        plt.grid(True)
        fig.savefig(local+'/'+options.variables+'_fullsim_boundaries_quantiles.pdf')

#if not drawLimitsOnly :
    ## doint Limits
for nn, sourceL in enumerate(sourcesCards) :
    for nbins in binstoDo :
        fileCardOnlyL = sourceL.split("/")[len(sourceL.split("/")) -1]
        fileCardOnlynBinL = "%s_%s%s" % (fileCardOnlyL, str(nbins), nameOutFileAdd)
        fileCardL = "%s/%s" % (mom_datacards, fileCardOnlynBinL)
        print ("make limit for %s.txt" % fileCardL)
        runCombineCmd("cp %s.txt %s.txt" % (sourceL, fileCardL))
        with open("%s.txt" % fileCardL,'r+') as ff:
            filedata = ff.read()
            filedata = filedata.replace(fileCardOnlyL, fileCardOnlynBinL)
            ff.truncate(0)
            ff.write(filedata)
        if drawLimitsOnly:    
            cmd = "combineTool.py  -M AsymptoticLimits  -t -1 %s.txt " % (fileCardL)
            if sendToCondor :
                cmd += ToSubmit + " %s_%s%s " % ()
            runCombineCmd(cmd,  local, "%s.log" % fileCardL)

            if nbins in info["makePlotsBin"] :
                # make only HH be considered signal (independent of the card marking)
                FolderOut = "%s/results/" % mom_datacards
                proc=subprocess.Popen(["mkdir %s" % FolderOut],shell=True,stdout=subprocess.PIPE)
                out = proc.stdout.read()

                cmd = "text2workspace.py"
                cmd += " %s.txt  " % (fileCardOnlynBinL)
                cmd += " -o %s/%s_WS.root" % (FolderOut, fileCardOnlynBinL)
                runCombineCmd(cmd, mom_datacards)
                print ("done %s/%s_WS.root" % (FolderOut, fileCardOnlynBinL))

                cmd = "combineTool.py -M FitDiagnostics "
                cmd += " %s_WS.root" % fileCardOnlynBinL
                #if blinded :
                #    cmd += " -t -1 "
                cmd += " --saveShapes --saveWithUncertainties "
                cmd += " --saveNormalization "
                cmd += " --skipBOnlyFit "
                cmd += " -n _shapes_combine_%s" % fileCardOnlynBinL
                runCombineCmd(cmd, FolderOut)
                fileShapes = glob.glob("%s/fitDiagnostics_shapes_combine_%s*root" % (FolderOut, fileCardOnlynBinL))[0]
                print ( "done %s" % fileShapes )

                savePlotsOn = "%s/plots/" % (mom_datacards)
                cmd = "mkdir %s" % savePlotsOn
                runCombineCmd(cmd)

                plainBins = False
                cmd = "python test/makePlots.py "
                cmd += " --input  %s" % fileShapes
                cmd += " --odir %s" % savePlotsOn
                #if doPostFit         :
                #    cmd += " --postfit "
                if not plainBins :
                    cmd += " --original %s/%s.root"        % (mom_datacards, fileCardOnlynBinL)
                cmd += " --era %s" % str(era)
                cmd += " --nameOut %s" % fileCardOnlynBinL
                #cmd += " --do_bottom "
                cmd += " --channel %s" % channel
                cmd += " --HH --binToRead HH_%s --binToReadOriginal  HH_%s " % (channel, channel)
                #cmd += "--nameLabel %s --labelX %s" % (toRead.replace(filebegin, ""), toRead.replace(filebegin, ""))
                #if not blinded         :
                #cmd += " --unblind  "
                cmd += " --signal_type %s "      % signal_type
                cmd += " --mass %s "             % mass
                cmd += " --HHtype %s --do_bottom"           % HHtype
                plotlog = "%s/%s_plot.log" % (savePlotsOn, fileCardOnlynBinL)
                runCombineCmd(cmd, '.', plotlog)

                didPlot = False
                for line in open(plotlog):
                    if '.pdf' in line and "saved" in line :
                        print(line)
                        didPlot = True
                        break
                if didPlot == False :
                    print ("!!!!!!!!!!!!!!!!!!!!!!!! The makePlots did not worked, to debug please check %s to see up to when the script worked AND run again for chasing the error:" % plotlog)
                    print(cmd)
                    #sys.exit()'''

#########################################
## make limits
print sources

if drawLimitsOnly :
    print "draw limits"
    fig, ax = plt.subplots(figsize=(5, 5))
    if BINtype == "quantiles" :
        namefig=local+'/'+options.variables+'_'+options.channel+'_'+signal_type +'_'+mass+'_'+options.subcats +'_fullsim_limits_quantiles' + "_do_signalFlat_" + str(options.do_signalFlat) + '_' + BDTfor+'_'+str(era)
    if BINtype == "regular" or BINtype == "mTauTauVis":
        namefig=local+'/'+options.variables+'_'+options.channel+'_fullsim_limits' + '_' + BDTfor
    if BINtype == "ranged" :
        namefig=local+'/'+options.variables+'_fullsim_limits_ranged'
    file = open(namefig+".csv","w")
    maxlimit =-99.
    for nn, source in enumerate(sourcesCards) :
        fileCardOnlyL = source.split("/")[len(source.split("/")) -1]
        print(fileCardOnlyL)
        limits = ReadLimits(
            fileCardOnlyL,
            binstoDo,
            BINtype,
            channel,
            mom_datacards,
            0, 0,
            sendToCondor,
            nameOutFileAdd
        )
        print (len(binstoDo),len(limits[0]))
        print 'binstoDo= ', binstoDo
        print limits[0]
        if max(limits[0]) > maxlimit : maxlimit = max(limits[0])
        for jj in limits[0] : file.write(unicode(str(jj)+', '))
        file.write(unicode('\n'))
        plt.plot(
            binstoDo,limits[0], color=colorsToDo[nn], linestyle='-',marker='o',
            label=bdtTypesToDoFile[nn].replace("output_NN_", "").replace("_withWZ", "").replace("3l_0tau", "") #.replace("mvaOutput_0l_2tau_deeptauVTight", "mva_legacy")
        )
        plt.plot(binstoDo,limits[1], color=colorsToDo[nn], linestyle='-')
        plt.plot(binstoDo,limits[3], color=colorsToDo[nn], linestyle='-')
    ax.legend(
        loc='upper left',
        fancybox=False,
        shadow=False ,
        ncol=1,
        fontsize=8
    )
    ax.set_xlabel('nbins')
    ax.set_ylabel('limits')
    maxsum=0
    maxlim = 1.5*maxlimit
    minlim = info["minlim"]
    plt.axis((min(binstoDo),max(binstoDo), minlim, maxlim))
    fig.savefig(namefig+'_ttH.png')
    fig.savefig(namefig+'_ttH.pdf')
    file.close()
    print ("saved",namefig)

