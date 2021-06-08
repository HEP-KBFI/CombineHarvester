#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
ROOT.gROOT.SetBatch(True)
import CMS_lumi, tdrstyle
from collections import OrderedDict


from optparse import OptionParser
from create_makefile_dependency import *
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path to the datacard")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path of where the GOF results and plot should be saved ")
parser.add_option("--signal_type", type="string", dest="signal_type", help="The scenario name e.g. nonResLO_SM")
parser.add_option("--channel", type="string", dest="channel", help="The multilepton channel, either 0l_4tau, 1l_3tau, 2lss, 2l_2tau, 3l, 3l_1tau, 4l")
parser.add_option("--era", type="string", dest="era", help="The data taking period.")
parser.add_option("--minx", type="int", dest="minx", help="min x")
parser.add_option("--maxx", type="int", dest="maxx", help="max x")
parser.add_option("--ntoys", type="int", dest="ntoys", help="total # of toys to be generated", default=500)
parser.add_option("--ntoys_perrun", type="int", dest="ntoys_perrun", help="total # of toys per run to be generated", default=50)
parser.add_option("--skipCombine", action='store_true',dest="skipCombine", default=False)
(options, args) = parser.parse_args()
inputPath = options.inputPath
outPath = options.outPath
signal_type = options.signal_type
channel = options.channel
era = options.era
ntoys = options.ntoys
skipCombine=options.skipCombine
minx=options.minx
maxx=options.maxx
ntoys = options.ntoys
ntoys_perrun = options.ntoys_perrun
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()

dir_ = "create_make_files"
proc=subprocess.Popen(['mkdir %s' % dir_],shell=True,stdout=subprocess.PIPE)
makefile = os.path.join(dir_+"/Makefile_GOF_%s_%s_%s" %(channel, era, signal_type))
stderr_file_path = os.path.join(dir_+"/Makefile_GOF_%s_%s_%s_stderr.log" %(channel, era, signal_type))
stdout_file_path = os.path.join(dir_+"/Makefile_GOF_%s_%s_%s_stdout.log" %(channel, era, signal_type))
phoniesToAdd = []
filesToClean = []
lines =[]

nrun = ntoys/ntoys_perrun

target = 'GOF_data'
#cmd = "combine -M GoodnessOfFit -d combine/800_spin0_lbn_1l_0tau_2016_res_WS.root --algo=saturated -n _%s_%s_%s_data -m 125 --setParametersForFit mask_HH_resolved_2b=1,mask_HH_resolved_1b=1,mask_HH_boosted=1 --setParametersForEval mask_HH_resolved_1b=0,mask_HH_resolved_2b=0,mask_HH_boosted=0 --freezeParameters r --setParameters r=0,mask_HH_resolved_2b=1,mask_HH_resolved_1b=1,mask_HH_boosted=1" %(channel, era, signal_type)
cmd = "combine -M GoodnessOfFit -d combine/800_spin0_lbn_1l_0tau_2016_res_WS.root --algo=saturated -n _%s_%s_%s_data -m 125" %(channel, era, signal_type)
phoniesToAdd.append(target)
lines.append("%s: " %target)
lines.append("\t%s" %cmd)
lines.append("\t")

mv_target='mv_data'
cmd = "mv higgsCombine_%s_%s_%s_data.GoodnessOfFit.mH125.root %s"%(channel, era, signal_type, outPath)
phoniesToAdd.append(mv_target)
lines.append("%s:%s " %(mv_target, target))
lines.append("\t%s" %cmd)
lines.append("\t")

tree_index=1
for run in range(1,nrun+1):
   target = 'run_toy_%s' %run
   tree_name = '_%s_%s_%s_toys_%s-%s' %(channel, signal_type, era, tree_index, tree_index+ntoys_perrun)
   #cmd = "combine -M GoodnessOfFit --algo=saturated -d combine/800_spin0_lbn_1l_0tau_2016_res_WS.root -n %s -m 125 --setParametersForFit mask_HH_resolved_2b=1,mask_HH_resolved_1b=1,mask_HH_boosted=1 --setParametersForEval mask_HH_resolved_1b=0,mask_HH_resolved_2b=0,mask_HH_boosted=0 --freezeParameters r --setParameters r=0,mask_HH_resolved_2b=1,mask_HH_resolved_1b=1,mask_HH_boosted=1 -t %s --toysFreq --seed %s" %(tree_name, ntoys_perrun, run)
   cmd = "combine -M GoodnessOfFit --algo=saturated -d combine/800_spin0_lbn_1l_0tau_2016_res_WS.root -n %s -m 125 -t %s --toysFreq --seed %s" %(tree_name, ntoys_perrun, run)
   phoniesToAdd.append(target)
   lines.append("%s: " %(target))
   lines.append("\t%s" %cmd)
   lines.append("\t")
   mv_target = 'mv_toy_%s' %run
   cmd = "mv higgsCombine%s.GoodnessOfFit.mH125.%s.root %s"%(tree_name, str(run), outPath)
   phoniesToAdd.append(mv_target)
   lines.append("%s:%s " %(mv_target, target))
   lines.append("\t%s" %cmd)
   lines.append("\t")
   tree_index += ntoys_perrun

createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
         (makefile, 17, stderr_file_path, stdout_file_path),
         False
)

hadd_toy_file_name =  '%s/higgsCombine_%s_%s_%s_toys.GoodnessOfFit.mH125.root' %(outPath, channel, signal_type, era)
cmd = "hadd -f %s %s/higgsCombine_%s_%s_%s_toys_*.GoodnessOfFit.mH125.*.root" %(hadd_toy_file_name, outPath, channel, signal_type, era)
print cmd
p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
comboutput = p.communicate()[0]
print 'done hadd' 

toys_file = ROOT.TFile("%s" %(hadd_toy_file_name))
#toys_file = ROOT.TFile("/home/snandan/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/gof.root")
#toys_file = ROOT.TFile("combine/gof/higgsCombine_1l_0tau_resonant_2017_toys.GoodnessOfFit.root")
print toys_file
toys_tree = toys_file.Get("limit")

data_file = ROOT.TFile("%s/higgsCombine_%s_%s_%s_data.GoodnessOfFit.mH125.root"%(outPath,channel, era, signal_type))
data_tree = data_file.Get("limit")


W = 800
H  = 600
T = 0.08*H
B = 0.12*H
L = 0.12*W
R = 0.04*W
c = ROOT.TCanvas("c","c",100,100,W,H)
c.SetFillColor(0)
c.SetBorderMode(0)
c.SetFrameFillStyle(0)
c.SetFrameBorderMode(0)
c.SetLeftMargin( L/W )
c.SetRightMargin( R/W )
c.SetTopMargin( T/H )
c.SetBottomMargin( B/H )
c.SetTickx(0)
c.SetTicky(0)
c.SetGrid()
c.cd()

toys = ROOT.TH1D("toys","toys",100,minx,maxx)
data = ROOT.TH1D("data","data",100,minx,maxx)
toys.SetLineWidth(3)
toys_tree.Draw("limit>>toys")
data_tree.Draw("limit>>data")
mean = data.GetMean()
toys.Scale(1/toys.Integral())
toys.SetTitle("; Goodnes of Fit (saturated); normalized entries")
toys.GetYaxis().SetTitleOffset(1.)
#toys=ROOT.gROOT.FindObject("toys")
toys.Draw("hist")
c.Update()
line = ROOT.TLine(mean,0,mean,toys.GetMaximum())
line.SetLineColor(ROOT.kRed)
line.SetLineWidth(3)
line.Draw("same")
line.SetLineColor(ROOT.kRed)
CMS_lumi.lumi_sqrtS = "bbww %s %s (%s)"%(channel, era, signal_type)
CMS_lumi.CMS_lumi(c,0,11)
ROOT.gPad.SetTicks(1,1)
pvalue=toys.Integral(toys.FindBin(mean), -1)
x1 = 0.7
x2 = 0.9
y2 = 0.85
y1 = 0.6
legend = ROOT.TLegend(x1,y1,x2,y2)
legend.SetFillStyle(0)
legend.SetBorderSize(0)
legend.SetTextSize(0.041)
legend.SetTextFont(42)
legend.AddEntry(line, "data (%s)"%(str(round(data.GetMean(),2))),'l')
legend.AddEntry(toys, "toys (%s)"%(str(round(toys.GetMean(),2))),'l')
legend.AddEntry(None, "p-value: %s"%(str(pvalue)),'')
legend.Draw()
c.SaveAs("%s/gof_%s_%s_%s.pdf"%(outPath, channel, era, signal_type))
c.SaveAs("%s/gof_%s_%s_%s.root"%(outPath, channel, era, signal_type))
c.Close()

