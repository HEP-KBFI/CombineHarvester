#!/usr/bin/env python
import os, subprocess, sys
workingDir = os.getcwd()
import os, re, shlex
from ROOT import *
import numpy as np


import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
# ./rebin_datacards.py --channel "4l_0tau"  --BINtype "regular" --doLimits
from io import open

exec(open(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager.py").read())
#execfile("../python/data_manager.py")

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--channel ", type="string", dest="channel", help="The ones whose variables implemented now are:\n   - 1l_2tau\n   - 2lss_1tau\n It will create a local folder and store the report*/xml", default="2lss_1tau")
parser.add_option("--variables", type="string", dest="variables", help="Add convention to file name", default="teste")
parser.add_option("--BINtype", type="string", dest="BINtype", help="regular / ranged / quantiles", default="regular")
parser.add_option("--doPlots", action="store_true", dest="doPlots", help="If you call this will not do plots with repport", default=False)
parser.add_option("--drawLimits", action="store_true", dest="drawLimits", help="If you call this will not do plots with repport", default=False)
parser.add_option("--doLimits", action="store_true", dest="doLimits", help="If you call this will not do plots with repport", default=False)
(options, args) = parser.parse_args()

doLimits   = options.doLimits
drawLimits = options.drawLimits
doPlots    = options.doPlots
channel    = options.channel
BINtype    = options.BINtype

#if not doLimits : from pathlib2 import Path

if channel == "2lss_1tau" : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2lss_1tau_datacards.py")
if channel == "1l_2tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_1l_2tau_datacards.py")
if channel == "1l_1tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_1l_1tau_datacards.py")
if channel == "2l_2tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2l_2tau_datacards.py")
if channel == "3l_1tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_3l_1tau_datacards.py")
if channel == "0l_2tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_0l_2tau_datacards.py")
if channel == "2lss_0tau" : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2lss_0tau_datacards.py")
if channel == "4l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_4l_0tau_datacards.py")
if channel == "3l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_3l_0tau_datacards.py")
if channel == "2los_1tau" : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2los_1tau_datacards.py")
if channel == "2l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2l_0tau_datacards.py")
if channel == "1l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_1l_0tau_datacards.py")

if channel == "hh_bb2l"   : sys.exit("Please make the corresponding input card")
if channel == "hh_bb1l"   : sys.exit("Please make the corresponding input card")

info = read_from()
print ("/afs/cern.ch/work/a/acarvalh/CMSSW_10_2_10/src/tth-bdt-training/python/data_manager.py")

sendToCondor = False
ToSubmit = " "
if sendToCondor :
    ToSubmit = " --job-mode condor --sub-opt '+MaxRuntime = 1800' --task-name"

sources=[]
bdtTypesToDo=[]
bdtTypesToDoLabel=[]
bdtTypesToDoFile=[]

import shutil,subprocess
proc=subprocess.Popen(["mkdir deeptauWPS/" + info["label"]],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()
proc=subprocess.Popen(["mkdir deeptauWPS/" + info["label"] + "/prepareDatacards_rebined"],shell=True,stdout=subprocess.PIPE)
#proc=subprocess.Popen(["mkdir deeptauWPS/" + info["label"] + "/datacard_rebined"],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()
#local = workingDir + "/deeptauWPS/" + info["label"]
#local = workingDir + "/deeptauWPS/" + info["label"] + "/prepareDatacards_rebined"
#local = "/home/acaan/CMSSW_10_2_13/src/cards_set/hh_bbww_nonres_prepare_datacards_rebined/"
#local = "/home/acaan/CMSSW_10_2_13/src/cards_set/hh_bbww_nonres_prepare_datacards_rebined_SL_AK8/"
#local = "/home/acaan/CMSSW_10_2_13/src/cards_set/hh_bbww_nonres_prepare_datacards_rebined_SL_AK8_LS/"
local = "/home/acaan/CMSSW_10_2_13/src/cards_set/hh_bbww_hh_bb1l_24Jun_SM_default_AK8_LS_fluxogramLike/"

print (info["bdtTypes"])

counter=0
for ii, bdtType in enumerate(info["bdtTypes"]) :
    fileName = info["mom"] + "/prepareDatacards_" + info["ch_nickname"] + "_" + bdtType + ".root"
    source=local+"/prepareDatacards_" + info["ch_nickname"] + "_" + bdtType
    print (fileName)
    if os.path.isfile(fileName) :#my_file.exists() :
        proc=subprocess.Popen(['cp ' + fileName + " " + local],shell=True,stdout=subprocess.PIPE)
        out = proc.stdout.read()
        sources = sources + [source]
        bdtTypesToDo = bdtTypesToDo +[channel+" "+bdtType]
        bdtTypesToDoLabel = bdtTypesToDoLabel +[channel+" "+bdtType]
        bdtTypesToDoFile=bdtTypesToDoFile+[bdtType] # info["ch_nickname"] +"_"+
        ++counter
        print ("rebinning ",sources[counter])
    else : print ("does not exist ",source)
bdtTypesToDoLabel = list(set(bdtTypesToDoLabel))
print ("I will rebin", bdtTypesToDoLabel,"(",len(sources),") BDT options")

if BINtype == "regular" or BINtype == "ranged" : binstoDo = info["nbinRegular"]
if BINtype == "quantiles" : binstoDo = info["nbinQuant"]
if BINtype == "none" : binstoDo=np.arange(1, info["originalBinning"])
print binstoDo

colorsToDo=['r','g','b','m','y','c', 'fuchsia', "peachpuff",'k','orange','y','c'] #['r','g','b','m','y','c','k']
if not doLimits and not drawLimits:
    #########################################
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
    for nn,source in enumerate(sources) :
        errOcont = rebinRegular(
            source,
            binstoDo,
            BINtype,
            info["originalBinning"],
            doPlots,
            bdtTypesToDo[nn],
            info["withFolder"]
            )
        if max(errOcont[2]) > maxplot : maxplot = max(errOcont[2])
        print bdtTypesToDo[nn]
        lastQuant=lastQuant+[errOcont[4]]
        xmaxQuant=xmaxQuant+[errOcont[5]]
        xminQuant=xminQuant+[errOcont[6]]
        bin_isMoreThan02 = bin_isMoreThan02 + [errOcont[7]]

        print (binstoDo,errOcont[2])
        plt.plot(binstoDo, errOcont[2], color=colorsToDo[ncolor],linestyle=linestyletype,label=bdtTypesToDo[nn].replace("ttH_1l_2tau","BDT PAS").replace("output_NN_","NN_").replace("_ttH_tH_3cat_","").replace("1l_2tau","").replace("2lss_1tau_","").replace("_1tau","").replace("2lss","").replace("__","_"))  #.replace("3l_0tau output_NN_3l_ttH_tH_3cat_v8_", "") ) # ,label=bdtTypesToDo[nn]
        #plt.plot(binstoDo, errOcont[2], color=colorsToDo[ncolor],linestyle=linestyletype,marker='o',label=bdtTypesToDo[nn].replace("2lss_0tau output_NN_2lss_ttH_tH_4cat_onlyTHQ_v4_", "") ) #
        ncolor = ncolor + 1
        if ncolor == 10 :
            ncolor = 0
            ncolor2 = ncolor2 + 1
            if ncolor2 == 0 : linestyletype = "-"
            if ncolor2 == 1 : linestyletype = "-."
            if ncolor2 == 2 : linestyletype = ":"
        #plt.plot(binstoDo,errOcont[2], color=colorsToDo[nn],linestyle='--',marker='x')
        ax.set_xlabel('nbins')
    #if BINtype == "regular" : maxplot = 0.3 #0.02
    #elif BINtype == "mTauTauVis" : maxplot=200.
    #else : maxplot =1.0 # 0.35
    maxplot = 1.2
    plt.axis((min(binstoDo),max(binstoDo),0,maxplot*1.2))
    #line_up, = plt.plot(binstoDo,linestyle='-',marker='o', color='k',label="fake-only")
    #line_down, = ax.plot(binstoDo,linestyle='--',marker='x', color='k',label="fake+ttV+EWK")
    #legend1 = plt.legend(handles=[line_up], loc='best') # , line_down
    ax.set_ylabel('err/content last bin')
    ax.legend(loc='best', fancybox=False, shadow=False, ncol=1, fontsize=8)
    plt.grid(True)
    namefig = local + '/' + options.variables + '_ErrOcont_' + BINtype + '.pdf'
    fig.savefig(namefig)
    print ("saved",namefig)
    print (bin_isMoreThan02)
    #########################################
    ## plot quantiles boundaries
    if BINtype == "quantiles" :
        ncolor = 0
        fig, ax = plt.subplots(figsize=(5, 5))
        plt.title(BINtype+" binning "+options.variables)
        #colorsToDo=['r','g','b','m','y','c']
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

if doLimits :
    if BINtype == "regular"   : doBins = info["nbinRegular"]
    if BINtype == "quantiles" : doBins = info["nbinQuant"]
    for nn, source in enumerate(sources) :
      for nbin in doBins :
        if BINtype == "regular" :
            inputbin = source + "_" + str(nbin) + "bins"
            outbin =  source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]) + "_" + str(nbin) + "bins"
        else :
            inputbin = source + "_" + str(nbin) + "bins_" + BINtype
            outbin =  source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]) + "_" + str(nbin) + "bins_" + BINtype
        if BINtype == "regular" :
            outfile = "%s_%s.log" % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin)+"bins")
        if BINtype == "quantiles" or BINtype == "ranged":
            outfile = "%s_%s.log" % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin)+"bins_"+BINtype )

        cmd = "WriteDatacards.py "
        cmd += "--inputShapes %s.root " % (inputbin)
        cmd += "--channel %s " % channel
        cmd += "--cardFolder %s " % local
        cmd += "--noX_prefix --era 2017  --no_data --analysis HH " # --only_ttH_sig --only_BKG_sig --only_tHq_sig --fake_mc
        runCombineCmd(cmd)
        if 0 > 1 :
            ######################
            cmd = "text2workspace.py  "
            cmd += " %s.txt " % (outbin)
            cmd += "-o %s_WS.root " % (outbin)
            cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose    --PO 'map=.*/ttH.*:r_ttH[1,-1,3]' "
            runCombineCmd(cmd, local)
            ######################
            cmd = "combine -M AsymptoticLimits  "
            cmd += "%s_WS.root " % (outbin)
            cmd += "  -t -1  --setParameters r_ttH=1,r_tH=1 --redefineSignalPOI r_ttH -n from0_r_ttH "
            runCombineCmd(cmd, local, str(outfile))
            runCombineCommand(combinecmd, card, verbose=False, outfolder=".", queue=None, submitName=None)
            """
            text2workspace.py datacard_0l_2tau_0l_2tau_mva_Updated.txt -o /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/0l_2tau_central_deepVSjVTight_veto_master_cards_2019Oct09_2018//results//datacard_0l_2tau_0l_2tau_mva_Updated_WS.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose    --PO 'map=.*/ttH.*:r_ttH[1,-1,3]
            combine -M AsymptoticLimits  datacard_0l_2tau_0l_2tau_mva_Updated_WS.root  -t -1  --setParameters r_ttH=1,r_tH=1 --redefineSignalPOI r_ttH -n from0_r_ttH
            """
        else :
            #######################
            cmd = "combineTool.py  -M AsymptoticLimits  -t -1 "
            if BINtype == "regular" :
                cmd += "%s_%s.txt " % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin) + "bins_mod")
            else :
                cmd += "%s_%s.txt " % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin) + "bins_" + BINtype)
            #cmd += " --setParameters r_ttH=1 --redefineSignalPOI r_ttH "
            if BINtype == "regular" :
                outfile = "%s_%s.log" % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin)+"bins_mod")
            if BINtype == "quantiles" :
                outfile = "%s_%s.log" % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin)+"bins_"+BINtype )
            if BINtype == "ranged" :
                outfile = "%s_%s.log" % (source.replace("prepareDatacards_" + info["ch_nickname"], "datacard_" + info["ch_nickname"]), str(nbin)+"bins_"+BINtype )
            if sendToCondor :
                cmd += ToSubmit + " " + bdtTypesToDo[nn].replace(channel+" ", "") + "_" + str(nbin)+"bins_"+BINtype
            runCombineCmd(cmd,  local, str(outfile))

#########################################
## make limits
print sources
if drawLimits :
    print "do limits"
    fig, ax = plt.subplots(figsize=(5, 5))
    if BINtype == "quantiles" : namefig=local+'/'+options.variables+'_fullsim_limits_quantiles'
    if BINtype == "regular" or BINtype == "mTauTauVis":
        namefig=local+'/'+options.variables+'_'+options.channel+'_fullsim_limits'
    if BINtype == "ranged" : namefig=local+'/'+options.variables+'_fullsim_limits_ranged'
    file = open(namefig+".csv","w")
    #maxlim =-99.
    for nn, source in enumerate(sources) :
        print(bdtTypesToDoFile[nn])
        limits=ReadLimits(bdtTypesToDoFile[nn], binstoDo, BINtype, channel, local, 0, 0, sendToCondor)
        #print (source, limits)
        print (len(binstoDo),len(limits[0]))
        print 'binstoDo= ', binstoDo
        print limits[0]
        for jj in limits[0] : file.write(unicode(str(jj)+', '))
        file.write(unicode('\n'))
        plt.plot(
            binstoDo,limits[0], color=colorsToDo[nn], linestyle='-',marker='o',
            label=bdtTypesToDoFile[nn].replace("output_NN_", "").replace("_withWZ", "").replace("3l_0tau", "") #.replace("mvaOutput_0l_2tau_deeptauVTight", "mva_legacy")
            )
        plt.plot(binstoDo,limits[1], color=colorsToDo[nn], linestyle='-')
        plt.plot(binstoDo,limits[3], color=colorsToDo[nn], linestyle='-')
        #if maxlim < max(limits[3]) : maxlim = max(limits[3])
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
    if channel in ["0l_2tau", "1l_0tau", "4l_0tau", "2los_1tau", "hh_bb2l"] :
        maxlim = 35.1
        minlim = 2.0
    elif channel in ["hh_bb1l"] : maxlim = 200.
    elif channel in ["2l_2tau"] :
        maxlim = 5.9
        minlim = 0.4
    else :
        #maxlim = 65. #1.6
        #minlim = 20.
        #maxlim = 110. #1.6
        #minlim = 40.
        #maxlim = 1.6
        #minlim = 0.4
        maxlim = 300.5
        minlim = 0.4
        #maxlim = 19.
        #minlim = 4.0
    plt.axis((min(binstoDo),max(binstoDo), minlim, maxlim))
    #plt.text(0.3, 1.4, BINtype+" binning "+" "+options.variables )
    fig.savefig(namefig+'_ttH.png')
    fig.savefig(namefig+'_ttH.pdf')
    file.close()
    print ("saved",namefig)
