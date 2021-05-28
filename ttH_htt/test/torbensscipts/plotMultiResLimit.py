#!/usr/bin/env pythono
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
parser.add_option("--spinCase", type="string", dest="spinCase", help="spin case")
parser.add_option("--ylabel", type="string", dest="ylabel", help="plot label")
parser.add_option("--scanlabels", type="string", dest="scanlabels", help="scan labels seperated by :")
parser.add_option("--log", action='store_true',dest="logy", default=False)
parser.add_option("--min", type="float", dest="miny", help="min y", default = 0.0)
parser.add_option("--max", type="float", dest="maxy", help="max y", default = 0.0)
parser.add_option("--unblind", action='store_true',dest="unblind", default=False)
(options, args) = parser.parse_args()
inputPaths = options.inputPaths
scanlabels = options.scanlabels
outPath = options.outPath
spinCase = options.spinCase
ylabel = options.ylabel
logy = options.logy
miny = options.miny
maxy = options.maxy
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
    tgraphs = []
    tgraphs_observed = []
    up2s = [ ]
    colors =  [ROOT.kBlack,ROOT.kBlue,ROOT.kRed,41,ROOT.kGray+1,ROOT.kMagenta+2,ROOT.kOrange+7,ROOT.kCyan+2]
    markers = [20,21,22,23,24,25,26,32]
    if len(resultdicts)==2:
        markers=[23,24]
    for k,r in enumerate(resultdicts):
        values = []
        for key in r.keys():
            values.append(int(key))
        N = len(values)
        values = sorted(values)
        median = ROOT.TGraph(N)      # median line
        observed = ROOT.TGraph(N)      # observed line
        i = 0
        for v in values:
            limit = r[str(v)]
            if unblind and len(limit)<6:
                raise Exception("Not enougth entries in limit to unblind")
            up2s.append(limit[2])
            if unblind:
                observed.SetPoint(    i,    values[i], limit[5] ) # observed
            median.SetPoint(    i,    values[i], limit[2] ) # median
            i = i + 1
        tgraphs.append(median)
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
    c.SetBottomMargin( B/H )
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
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    frame.GetYaxis().SetTitle("95% upper limit on #sigma (#Chi#rightarrow HH) [pb]")
    frame.GetXaxis().SetTitle(xlabel)
    frame.SetMinimum(miny)
    frame.SetMaximum(max(up2s)*1.05)
    if logy:
        frame.SetMaximum(max(up2s)*15)
    frame.GetXaxis().SetLimits(min(values),max(values))
    if logy:
        c.SetLogy()
    if(maxy>0.): frame.SetMaximum(maxy)
    tgraphs[0].Draw()
    for i, g in enumerate(tgraphs):
        g.SetLineColor(colors[i])
        print scanlabels.split(":")[i], markers[i]
        g.SetMarkerColor(colors[i])
        g.SetMarkerStyle(markers[i])
        g.SetMarkerSize(1.2)
        if not unblind:
            g.SetLineWidth(2)
            g.Draw("PLSame")
        else:
            g.SetLineStyle(2)
            g.SetLineWidth(1)
            g.Draw("LSame")
    for i, g in enumerate(tgraphs_observed):
        g.SetLineColor(colors[i])
        print scanlabels.split(":")[i], markers[i]
        g.SetMarkerColor(colors[i])
        g.SetMarkerStyle(markers[i])
        g.SetMarkerSize(1.2)
        g.SetLineWidth(2)
        g.Draw("PLSame")
        
    CMS_lumi.lumi_sqrtS = ylabel
    CMS_lumi.CMS_lumi(c,0,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    #x1 = 0.459
    x1 = 0.3
    x2 = 0.959
    y2 = 0.9175
    y1 = 0.6675
    legend = ROOT.TLegend(x1,y1,x2,y2)
    #legend.SetFillStyle(0)
    #legend.SetFillColor(1)
    legend.SetNColumns(3)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    if unblind:
        for i,g in enumerate(tgraphs_observed):
            legend.AddEntry(g, scanlabels.split(":")[i],'PL')
        legend.AddEntry(tgraphs[0], 'expected','L')
    else:
        for i,g in enumerate(tgraphs):
            legend.AddEntry(g, scanlabels.split(":")[i],'PL')
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
plotUpperLimits(resultdicts, scanlabels, 'm#Chi [GeV] (%s)'%spinCase, ylabel, outPath)
