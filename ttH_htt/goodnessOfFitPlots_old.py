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
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path to the datacard")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path of where the GOF results and plot should be saved ")
parser.add_option("--signal_type", type="string", dest="signal_type", help="The scenario name e.g. nonResLO_SM")
parser.add_option("--channel", type="string", dest="channel", help="The multilepton channel, either 0l_4tau, 1l_3tau, 2lss, 2l_2tau, 3l, 3l_1tau, 4l")
parser.add_option("--era", type="string", dest="era", help="The data taking period.")
parser.add_option("--ntoys", type="int", dest="ntoys", help="Number of toys to be generated")
parser.add_option("--minx", type="int", dest="minx", help="min x")
parser.add_option("--maxx", type="int", dest="maxx", help="max x")
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
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()


commands = []
commands.append("combine -M GoodnessOfFit --algo=saturated %s -n _%s_%s_%s_data -m 125"%(inputPath, channel, era, signal_type))
commands.append("mv higgsCombine_%s_%s_%s_data.GoodnessOfFit.mH125.root %s"%(channel, era, signal_type, outPath))
commands.append("combine -M GoodnessOfFit --algo=saturated %s -n _%s_%s_%s_toys -m 125 -t %s --toysFreq"%(inputPath, channel, era, signal_type, ntoys))
commands.append("mv higgsCombine_%s_%s_%s_toys.GoodnessOfFit.mH125.123456.root %s"%(channel, era, signal_type, outPath))

if not skipCombine:
    for command in commands:
        print command
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line.rstrip("\n")
        print 'done'
        retval = p.wait()

toys_file = ROOT.TFile("%s/higgsCombine_%s_%s_%s_toys.GoodnessOfFit.mH125.123456.root"%(outPath,channel, era, signal_type))
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

toys = ROOT.TH1D("toys","toys",25,minx,maxx)
data = ROOT.TH1D("data","data",100,minx,maxx)
toys.SetLineWidth(3)
toys_tree.Draw("limit>>toys")
data_tree.Draw("limit>>data")
mean = data.GetMean()
toys.Scale(1/toys.Integral())
toys.SetTitle("; Goodnes of Fit (saturated); normalized entries")
toys.GetYaxis().SetTitleOffset(1.)
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

