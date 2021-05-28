#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
ROOT.gROOT.SetBatch(True)
from collections import OrderedDict
import CMS_lumi, tdrstyle
from optparse import OptionParser
parser = OptionParser()


parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where combine results are")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path to store plot ")
parser.add_option("--ylabel", type="string", dest="ylabel", help="plot label")
parser.add_option("--log", action='store_true',dest="logy", default=False)
parser.add_option("--min", type="float", dest="miny", help="min y", default = 0.0)
parser.add_option("--unblind", action='store_true',dest="unblind", default=False)
parser.add_option("--BMcase", type="int", dest="BMcase", help="BMcase", default = 1)
(options, args) = parser.parse_args()
inputPath = options.inputPath
outPath = options.outPath
ylabel = options.ylabel
logy = options.logy
miny = options.miny
BMcase = options.BMcase
unblind = options.unblind
def getLimits(file_name): 
    print file_name
    file = ROOT.TFile(file_name)
    tree = file.Get("limit")
    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
    return limits[:6]

def plotUpperLimits(resultdict, xlabel, ylabel,outpath, BMcase):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    values = range(14)
    labels = ["","SM", "BM1", "BM2", "BM3", "BM4", "BM5", "BM6", "BM7", "BM8", "BM9", "BM10", "BM11", "BM12",]
    labels2= ["","SM", "BM1", "BM2", "BM3", "BM4", "BM5", "BM6", "BM7", "BM8", "BM9", "BM10", "BM11", "BM12",]
    if BMcase is 1:
        labels = ["","SM","JHEP04BM1","JHEP04BM2","JHEP04BM3","JHEP04BM4","JHEP04BM5","JHEP04BM6","JHEP04BM7","JHEP04BM8","JHEP04BM9","JHEP04BM10","JHEP04BM11","JHEP04BM12","JHEP04BM8a","JHEP03BM1","JHEP03BM2","JHEP03BM3","JHEP03BM4","JHEP03BM5","JHEP03BM6","JHEP03BM7","extrabox"]
        labels2=labels
    if BMcase is 2:
        labels = ["","SM","JHEP04BM1","JHEP04BM2","JHEP04BM3","JHEP04BM4","JHEP04BM5","JHEP04BM6","JHEP04BM7","JHEP04BM8","JHEP04BM9","JHEP04BM10","JHEP04BM11","JHEP04BM12","JHEP04BM8a"]
        labels2=labels
    if BMcase is 3:
        labels = ["","JHEP03BM1","JHEP03BM2","JHEP03BM3","JHEP03BM4","JHEP03BM5","JHEP03BM6","JHEP03BM7"]
        labels2=labels
    if BMcase is 4:
        labels = ["","JHEP03BM1","JHEP03BM2","JHEP03BM3","JHEP03BM4","JHEP03BM5","JHEP03BM6","JHEP03BM7","JHEP04BM8a"]
        labels2 =["", "JHEP04BM11","JHEP04BM11","JHEP04BM5","JHEP04BM3","JHEP04BM9","JHEP04BM3","JHEP04BM9","JHEP04BM9"]
    values = range(len(labels))
    limits = []
    limits2 = []
    for label in labels:
        if len(label)>0:
            limits.append(resultdict[label])
        if(label is ""):
            limits.append(resultdict["SM"])
    for label in labels2:
        if len(label)>0:
            limits2.append(resultdict[label])
        if(label is ""):
            limits2.append(resultdict["SM"])
    print labels
    N = len(values)
    yellow = ROOT.TGraph(2*N)    # yellow band
    green = ROOT.TGraph(2*N)     # green band
    median = ROOT.TGraph(N)      # median line
    median2 = ROOT.TGraph(N)      # median line
    observed = ROOT.TGraph(N)      # median line
    up2s = [ ]
    indx = 0
    for i in range(N):
        limit = limits[i]
        limit2 = limits2[i]
        if (unblind and (len(limit)<6 or len(limit2)<6)):
            raise Exception("Not enougth entries in limit to unblind")
        print limit[2]/limit2[2]
        up2s.append(limit[4])
        for j in range(100):
            indx = indx +1
            yellow.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[4] ) # + 2 sigma
            green.SetPoint(     indx,    values[i]-0.5+(j+1.)/100., limit[3] ) # + 1 sigma
            median.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[2] ) # median
            green.SetPoint(  2*N*100-1-indx, values[i]-0.5+(j+1.)/100., limit[1] ) # - 1 sigma
            yellow.SetPoint( 2*N*100-1-indx, values[i]-0.5+(j+1.)/100., limit[0] ) # - 2 sigma
            if unblind: 
                observed.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[5] ) # median
                median2.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit2[5] ) # median
            else:
                median2.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit2[2] ) # median

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
    c.SetBottomMargin( 1.5*B/H )
    c.SetTickx(0)
    c.SetTicky(0)
    c.SetGrid()
    c.cd()
    frame = c.DrawFrame(1.4,0.001, 4.1, 10)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetTitleOffset(1.4)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    frame.GetYaxis().SetTitle("95% upper limit on #sigma (pp#rightarrow HH) [pb]")
    frame.GetXaxis().SetTitle(xlabel)
    frame.SetMinimum(miny)
    frame.SetMaximum(max(up2s)*1.05)
    if logy:
        frame.SetMaximum(max(up2s)*15)
    frame.GetXaxis().SetLimits(min(values)+0.5,max(values)+0.5)
    for i,l in enumerate(labels):
        if l is "extrabox": l ='box'
        frame.GetXaxis().SetBinLabel(frame.GetXaxis().FindBin(i),l)
    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    observed.SetLineColor(ROOT.kBlack)
    observed.SetLineWidth(3)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
    yellow.Draw('F')
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')
    if logy:
        c.SetLogy()
    median.SetLineColor(1)
    median2.SetLineColor(ROOT.kRed)
    median2.SetLineWidth(3)
    median.SetLineWidth(2)
    median.SetLineStyle(2)
    median.Draw('Lsame')
    if unblind: observed.Draw('Lsame')
    if BMcase is 4:
        median2.Draw('Lsame')
    CMS_lumi.lumi_sqrtS = ylabel
    CMS_lumi.CMS_lumi(c,0,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
    x1 = 0.55
    x2 = x1 + 0.24
    y2 = 0.86
    y1 = 0.70
    legend = ROOT.TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    if BMcase is 4:
        if unblind:
            legend.AddEntry(median2, "mapped BM (observed)",'L')
        else:
            legend.AddEntry(median2, "mapped BM",'L')
    if unblind: legend.AddEntry(observed, "Asymptotic CL_{s} observed",'L')
    legend.Draw()
    print " "
    c.SaveAs(outpath)
    c.SaveAs(outpath.replace('.pdf','.root'))
    c.Close()
 

# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()

listproc = glob.glob( "%s/*.root" % inputPath)
resultdict = {}
for result in listproc:
    mass = result.split('_')[-1].split('.')[0]
    resultdict[mass]=getLimits(result)
plotUpperLimits(resultdict, '', ylabel, outPath, BMcase)
