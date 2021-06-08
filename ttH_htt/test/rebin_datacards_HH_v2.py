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

functions = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager_rebin_datacards_mod.py"
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
parser.add_option("--do_signalFlat_only", action="store_true", dest="do_signalFlat_only", help="whether you want to make signal flat or total bkg flat", default=False)
parser.add_option("--output_path", type="string", dest="output_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--prepareDatacards_path", type="string", dest="prepareDatacard_path", help="Where to copy prepareDatacards and make subdiretories with results")
parser.add_option("--drawLimitsOnly", action="store_true", dest="drawLimitsOnly", help="If you call this will not do plots with repport", default=False)
parser.add_option("--doLimitsOnly", action="store_true", dest="doLimitsOnly", help="If you call this will not do plots with repport", default=False)
parser.add_option("--BDTfor", dest="BDTfor", help="type of BDT to be considered", default="SM")
parser.add_option("--shapeSyst",      action="store_true", dest="shapeSyst",   help="Do apply the shape systematics. Default: False", default=False)
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
    dest="subcats",
    help="subcategory to be considered in rebinning",
    default=''
    )
(options, args) = parser.parse_args()

doLimitsOnly   = options.doLimitsOnly
drawLimitsOnly = options.drawLimitsOnly
channel    = options.channel
BINtype    = options.BINtype
do_signalFlat = options.do_signalFlat
do_signalFlat_only = options.do_signalFlat_only
signal_type  = options.signal_type
mass         = options.mass
HHtype       = options.HHtype
era          = options.era
local        = options.output_path
mom          = options.prepareDatacard_path
BDTfor =  options.BDTfor
in_more_subcats = options.subcats
shape            = options.shapeSyst

## HH
if channel == "2l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_2l_0tau_datacards.py")
if channel == "1l_0tau"   : execfile(os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt//cards/info_1l_0tau_datacards.py")

info = read_from(in_more_subcats, BDTfor)
print ("Cards to rebin from %s" % channel)

sendToCondor = False
ToSubmit = " "
if sendToCondor :
    ToSubmit = " --job-mode condor --sub-opt '+MaxRuntime = 1800' --task-name"

import shutil,subprocess
proc=subprocess.Popen(["mkdir %s" % local],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()

output_dir = "%s/datacards_rebined/" % local
proc=subprocess.Popen(["mkdir %s" % output_dir],shell=True,stdout=subprocess.PIPE)
out = proc.stdout.read()
bdtType = info["bdtTypes"][0]
print (info["bdtTypes"])
if channel == '1l_0tau':
    addSyst = 'addSystFakeRates_'
elif channel == '2l_0tau':
    addSyst = 'addSystDYBgr_'

fileName = mom   + '/' + addSyst + info["ch_nickname"] + "_" + bdtType + ".root"
source   = local + '/' + addSyst + info["ch_nickname"] + "_" + bdtType
print (fileName)
if os.path.isfile(fileName) :
    proc              = subprocess.Popen(['cp ' + fileName + " " + local],shell=True,stdout=subprocess.PIPE)
    out = proc.stdout.read()
    bdtTypesToDo = channel+" "+bdtType
    bdtTypesToDoFile  = bdtType
    print ("rebinning ", source)
else : print ("does not exist ",source)

if 'HH_' in fileName:
    binsStart = 2
    binsEnd = 30
else:
    binsStart = 10
    binsEnd = 10

print ('binsToStart: '+ str(binsStart) + 'binsToEnd: ' + str(binsEnd))
### first we do one datacard.txt / bdtType
nameOutFileAdd = ""
if BINtype=="none" :
    nameOutFileAdd =  "bins_none"
if BINtype=="regular" or options.BINtype == "mTauTauVis":
    nameOutFileAdd =  "bins"
if BINtype=="ranged" :
    nameOutFileAdd =  "bins_ranged"
if BINtype=="quantiles" :
    nameOutFileAdd = "bins_quantiles"

def write_datacard(input, outputfile, channel, era, signal_type, mass, HHtype, subcat, shape=False):
    mass = mass.replace('_overlap', '')
    cmd = "WriteDatacards.py "                                                                                                         
    cmd += "--inputShapes %s " % (input)
    cmd += "--channel %s " % channel
    cmd += "--output_file %s " % outputfile
    cmd += "--noX_prefix --era %s --analysis HH " % (era) # --only_ttH_sig --only_BKG_sig --only_tHq_sig --fake_mc
    cmd += " --signal_type %s "      % signal_type
    cmd += " --mass %s "             % mass
    cmd += " --HHtype %s "           % HHtype
    cmd += " --subcat %s "           % subcat
    if shape:
        cmd += " --shapeSyst --forceModifyShapes "
    log_datacard = "%s_writedatacard.log" % (outputfile)
    runCombineCmd(cmd, ".", log_datacard)
    didCard = False
    for line in open(log_datacard):
        if "Output file:" in line :
            fileCard = line.split(" ")[3].replace("'","").replace(",","").replace(".txt","")
            print("done card %s.txt" % fileCard)
            didCard = True
            break
    if didCard == False :                                                                                                              
                print ("!!!!!!!!!!!!!!!!!!!!!!!! The WriteDatacards did not worked, to debug please check %s to see up to when the script work\ed AND run again for chasing the error:" % log_datacard) 
                print(cmd)
                sys.exit()

def limit_improved(limit, position):
    if abs(limit[position]-limit[len(limit)-1]) < 0.05*limit[position]:
        return False
    return True
colorsToDo=['r','g','b','m','y','c', 'fuchsia', "peachpuff",'k','orange','y','c'] #['r','g','b','m','y','c','k']
#########################################
#if not (drawLimitsOnly or doLimitsOnly) :
ibin = 0
merge_Wjets = False
merge_DY = False
dataDY = False
if channel == '2l_0tau':
    merge_Wjets = True
    dataDY = True
elif channel == '1l_0tau':
    merge_DY = True
errOcontLast_all = [] 
bincontlast_all = []
central_limit = []
one_sigma_up = []
one_sigma_dn = []
nbins = []
for bin in range(binsStart, binsEnd+1, 2):
    rebinned, errOcontLast, bincontlast = rebinRegular_bbww(
        source,
        bin,
        BINtype,
        do_signalFlat,
        do_signalFlat_only,
        merge_Wjets,
        merge_DY,
        dataDY,
        signal_type,
        output_dir,
        nameOutFileAdd,
    )
    if rebinned:
        errOcontLast_all.append(errOcontLast)
        bincontlast_all.append(bincontlast)
        nbins.append(bin)
        input = '%s/%s%s_%s_%s%s.root' \
                %(output_dir, addSyst, info["ch_nickname"], bdtType, str(bin), nameOutFileAdd)
        outputfile = input.replace(addSyst, "datacard_").replace('.root', '')
        write_datacard(input, outputfile, channel, era, signal_type, mass, HHtype, options.subcats, False)
        if 'HH_' in fileName:
            cmd = "combineTool.py  -M AsymptoticLimits  -t -1 %s.txt " %outputfile
            runCombineCmd(cmd,  local, "%s_limit.log" % outputfile)
            limit = readLimit('%s_limit.log' %(outputfile))
            central_limit.append(limit[0])
            one_sigma_up.append(limit[1])
            one_sigma_dn.append(limit[2])
            if (len(central_limit) - ibin) ==5:
                improved = limit_improved(central_limit, ibin)
                ibin += 5
                if not improved:
                    break
    else:
        break
if 'HH_' in fileName:
    best_limit_index = central_limit.index(min(central_limit))
    print ('best limit found at bin ' + str(nbins[best_limit_index])\
           + 'with limit ' + str(central_limit[best_limit_index]))
    print errOcontLast_all, '\t', bincontlast_all, '\t', central_limit, '\t', nbins
else:
     best_limit_index = 0
print '***********', info["ch_nickname"], '\t', str(nbins[best_limit_index])
input = '%s/%s%s_%s_%s%s.root' \
        %(output_dir, addSyst, info["ch_nickname"], bdtType, str(nbins[best_limit_index]), nameOutFileAdd)
outputfile = input.replace(addSyst, "datacard_").replace('.root', '_%s_final' %signal_type)
outputfile_rm = glob.glob('%s/datacard_%s_%s_*%s_%s_final*' \
        %(output_dir, info["ch_nickname"], bdtType, nameOutFileAdd, signal_type))
for f in outputfile_rm:
    os.remove(f)
write_datacard(input, outputfile, channel, era, signal_type, mass, HHtype, options.subcats, True)
if (signal_type == 'nonresNLO' or signal_type == 'res') and drawLimitsOnly:
    if 'HH_' in fileName:
        fig, ax = plt.subplots(figsize=(5, 5))
        namefig=local+'/'+options.channel+'_'+signal_type +'_'+mass+'_'+options.subcats\
                 +'_limits_quantiles_do_signalFlat_' + str(options.do_signalFlat) + '_' + BDTfor+'_'+str(era)
        maxlimit = max(central_limit)
        plt.plot(
            nbins, central_limit, color=colorsToDo[0], linestyle='-',marker='o',
            label=info["ch_nickname"] + "_" + bdtType
        )
        plt.plot(nbins,one_sigma_up, color=colorsToDo[0], linestyle='-')
        plt.plot(nbins,one_sigma_dn, color=colorsToDo[0], linestyle='-')
        ax.legend(
            loc='upper left',
            fancybox=False,
            shadow=False ,
            ncol=1,
            fontsize=8
        )
        ax.set_xlabel('nbins')
        ax.set_ylabel('limits')
        maxlim = 1.5*maxlimit                                                                                                              
        minlim = info["minlim"]
        plt.axis((min(nbins),max(nbins), minlim, maxlim))                                                                                    
        fig.savefig(namefig+'.png') 
        fig.savefig(namefig+'.pdf')                                                                                                            
        print ("saved",namefig)
        fig, ax = plt.subplots(figsize=(5, 5))
        namefig=local+'/'+options.channel+'_'+signal_type +'_'+mass+'_'+options.subcats\
                 +'_errOcont_quantiles_do_signalFlat_' + str(options.do_signalFlat) + '_' + BDTfor+'_'+str(era)
        maxlimit = max(errOcontLast_all)
        plt.plot(
            nbins, errOcontLast_all, color=colorsToDo[0], linestyle='-',marker='o',
            label=info["ch_nickname"] + "_" + bdtType
        )
        ax.legend(
            loc='upper left',
            fancybox=False,
            shadow=False ,
            ncol=1,
            fontsize=8
        )
        ax.set_xlabel('nbins')
        ax.set_ylabel('errOcont')
        maxlim = 1.5*maxlimit
        minlim = info["minlim"]
        plt.axis((min(nbins),max(nbins), minlim, maxlim))
        fig.savefig(namefig+'.png')
        fig.savefig(namefig+'.pdf')
        print ("saved",namefig)
    datacard = 'datacard_%s_%s_%sbins_quantiles' %(info["ch_nickname"], bdtType, str(str(nbins[best_limit_index])))
    FolderOut = "%s/results/" % output_dir            
    proc=subprocess.Popen(["mkdir %s" % FolderOut],shell=True,stdout=subprocess.PIPE)                                          
    out = proc.stdout.read()
    cmd = "text2workspace.py %s.txt -o %s/%s_WS.root" %(datacard, FolderOut, datacard)
    runCombineCmd(cmd, output_dir)
    cmd = "combineTool.py -M FitDiagnostics "                                                                                  
    cmd += " %s/%s_WS.root" % (FolderOut, datacard)
    #if blinded :
    #cmd += " -t -1 "
    cmd += " --saveShapes --saveWithUncertainties "
    cmd += " --saveNormalization "
    cmd += " --skipBOnlyFit "
    cmd += " -n _shapes_combine_%s" % datacard
    runCombineCmd(cmd, FolderOut)
    fileShapes = glob.glob("%s/fitDiagnostics_shapes_combine_%s*root" % (FolderOut, datacard))[0]
    print ( "done %s" % fileShapes )
    savePlotsOn = "%s/plots/" % (output_dir)
    cmd = "mkdir %s" % savePlotsOn
    runCombineCmd(cmd)
    plainBins = False
    cmd = "python test/makePlots.py "
    cmd += " --input  %s" % fileShapes
    cmd += " --odir %s" % savePlotsOn
    #if doPostFit:                                                                                                             
    cmd += " --doPostFit "                                                                                                  
    if not plainBins :
        cmd += " --original %s/%s.root"        % (output_dir, datacard)
        cmd += " --era %s" % str(era)
        cmd += " --nameOut %s" % (datacard)
        #cmd += " --do_bottom "                                                                                                    
        cmd += " --channel %s" % channel
        cmd += " --HH --binToRead HH_%s --binToReadOriginal  HH_%s " % (channel, channel)
        #cmd += "--nameLabel %s --labelX %s" % (toRead.replace(filebegin, ""), toRead.replace(filebegin, ""))                      
        #if not blinded         :                                                                                                  
        #cmd += " --unblind  "                                                                                                     
        cmd += " --signal_type %s "      % signal_type
        cmd += " --mass %s "             % mass
        cmd += " --HHtype %s --do_bottom"           % HHtype
        if 'HH' not in fileName:
            cmd += " --unblind"
        plotlog = "%s/%s_plot.log" % (savePlotsOn, datacard)
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
