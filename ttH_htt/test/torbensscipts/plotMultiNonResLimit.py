#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
from collections import OrderedDict
import CMS_lumi, tdrstyle
from optparse import OptionParser
parser = OptionParser()


parser.add_option("--inputPaths", type="string", dest="inputPaths", help="Full path of where combine results are seperated by :")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path to store plot ")
parser.add_option("--ylabel", type="string", dest="ylabel", help="plot label")
parser.add_option("--log", action='store_true',dest="logy", default=False)
parser.add_option("--min", type="float", dest="miny", help="min y", default = 0.0)
parser.add_option("--scanlabels", type="string", dest="scanlabels", help="scan labels seperated by :")
parser.add_option("--BMcase", type="int", dest="BMcase", help="BMcase", default = 1)
parser.add_option("--unblind", action='store_true',dest="unblind", default=False)
(options, args) = parser.parse_args()
inputPaths = options.inputPaths
outPath = options.outPath
ylabel = options.ylabel
logy = options.logy
miny = options.miny
scanlabels = options.scanlabels
BMcase = options.BMcase
unblind = options.unblind
def getLimits(file_name): 
    file = ROOT.TFile(file_name)
    tree = file.Get("limit")
    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
    return limits[:6]

def plotUpperLimits(resultdicts, scanlabels, xlabel, ylabel,outpath):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    colors =  [ROOT.kBlack,ROOT.kBlue,ROOT.kRed,41,ROOT.kGray+1,ROOT.kMagenta+2,ROOT.kOrange+7,ROOT.kCyan+2]
    tgraphs = []
    tgraphs_observed = []
    tg_markers = []
    tgraphs2 = []
    tg_markers2 = []
    up2s = [ ]
    labels = ["","SM", "BM1", "BM2", "BM3", "BM4", "BM5", "BM6", "BM7", "BM8", "BM9", "BM10", "BM11", "BM12",]
    if BMcase is 1:
        labels = ["","SM","JHEP04BM1","JHEP04BM2","JHEP04BM3","JHEP04BM4","JHEP04BM5","JHEP04BM6","JHEP04BM7","JHEP04BM8","JHEP04BM9","JHEP04BM10","JHEP04BM11","JHEP04BM12","JHEP04BM8a","JHEP03BM1","JHEP03BM2","JHEP03BM3","JHEP03BM4","JHEP03BM5","JHEP03BM6","JHEP03BM7","extrabox"]
    if BMcase is 2:
        labels = ["","SM","JHEP04BM1","JHEP04BM2","JHEP04BM3","JHEP04BM4","JHEP04BM5","JHEP04BM6","JHEP04BM7","JHEP04BM8","JHEP04BM9","JHEP04BM10","JHEP04BM11","JHEP04BM12","JHEP04BM8a"]
    if BMcase is 3:
        labels = ["","JHEP03BM1","JHEP03BM2","JHEP03BM3","JHEP03BM4","JHEP03BM5","JHEP03BM6","JHEP03BM7"]
    for k,r in enumerate(resultdicts):
        values = range(len(labels))
        limits = []
        for label in labels:
            if len(label)>0:
                limits.append(r[label])
            if(label is ""):
                limits.append(r["SM"])
        N = len(values)
        median = ROOT.TGraph(N)      # median line
        markers = ROOT.TGraph(N)     # markers
        observed = ROOT.TGraph(N)      # observed line
        indx = 0
        for i in range(N):
            limit = limits[i]
            if unblind and len(limit)<6:
                raise Exception("Not enougth entries in limit to unblind")
            up2s.append(limit[4])
            if unblind:
                markers.SetPoint(i, i, limit[5])
            else:
                markers.SetPoint(i, i, limit[2])
            for j in range(100):
                indx = indx +1
                median.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[2] ) # median
                if unblind: observed.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[5] ) # observed
        tgraphs.append(median)
        tg_markers.append(markers)
        if unblind: tgraphs_observed.append(observed)
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
        frame.GetXaxis().SetBinLabel(frame.GetXaxis().FindBin(i),l)
    if logy:
        c.SetLogy()
        tgraphs[0].Draw()
    markers = [20,21,22,23,24,25,26,32]
    for i, g in enumerate(tgraphs):
        tg_markers[i].SetLineColor(colors[i])
        tg_markers[i].SetMarkerColor(colors[i])
        tg_markers[i].SetMarkerStyle(markers[i])
        tg_markers[i].SetMarkerSize(1.2)
        g.SetLineColor(colors[i])
        g.SetLineWidth(2)
        if unblind:
            g.SetLineWidth(1)
            g.SetLineStyle(2)
            tgraphs_observed[i].SetLineWidth(2)
            tgraphs_observed[i].SetLineColor(colors[i])
            tgraphs_observed[i].Draw("same")
        g.Draw("Same")
        tg_markers[i].Draw("PSame")
    CMS_lumi.lumi_sqrtS = ylabel
    CMS_lumi.CMS_lumi(c,0,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    x1 = 0.4
    x2 = 0.9
    y2 = 0.9
    y1 = 0.65
    legend = ROOT.TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetNColumns(3)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    for i,g in enumerate(tg_markers):
        legend.AddEntry(g, scanlabels.split(":")[i],'PL')
    if unblind:
        legend.AddEntry(tgraphs[0], 'expected','PL')
    legend.Draw()
    print " "
    c.SaveAs(outpath)
    c.Close()
 

# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()
resultdicts = []
for path in inputPaths.split(":"):
    listproc = glob.glob( "%s/*.root" % path)
    resultdict = {}
    for result in listproc:
        mass = result.split('_')[-1].split('.')[0]
        resultdict[mass]=getLimits(result)
    resultdicts.append(resultdict)

plotUpperLimits(resultdicts,scanlabels, '', ylabel, outPath)
